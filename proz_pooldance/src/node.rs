use std::cmp;
use std::collections::HashMap;
use std::collections::HashSet;
use std::num::Wrapping;
use std::sync::mpsc;
use std::time::{SystemTime, UNIX_EPOCH};
use std::{thread, time};

use rand::Rng;
use std::process;

use crate::network::{
    addr_str, find_peer, scan, worker_recv, worker_send, Domain, Package, Peer,
    Queue,
};
use crate::resource;
use crate::resource::{PairMessage, Resource};

// Aby moc uzywac jak Python-owy `dict`
macro_rules! hashmap {
    ($( $key: expr => $val: expr ),*) => {{
         let mut map = ::std::collections::HashMap::new();
         $( map.insert($key, $val); )*
         map
    }}
}

// This returns a cloned HashMap
// because Rust uses the Clone-implementation on HashMap
fn do_clone<K: Clone, V: Clone>(data: &HashMap<K, V>) -> HashMap<K, V> {
    data.clone()
}

pub struct Node {
    // === base === //
    pub id: Peer,                             // kim jestesmy?
    queue_recv: Queue,                        // kolejka: na wysylanie
    queue_send: Queue,                        // kolejka: na odbior
    domains: Vec<Domain>,                     // nasz infra-net
    peers: HashSet<Peer>,                     // kto jest aktywny
    pub resources: HashMap<String, Resource>, // jakie zasoby w puli

    // === resource algo. === //
    wants: HashMap<String, i32>, // WYMAGANIA: aby moc zatanczyc w parze
    pseudo_have: HashMap<String, i32>, // co mysli ze ma (cache-aware)
    transfer_luck: i32,          // unicorn variable (algorytm kradzenia)

    // === pairing algo. === //
    sex: i32,                           // wybor plci (kobieta/mezczyzna)
    paired_with: i32,                   // zatwierdzony ID pary
    pseudo_paired: i32,                 // z kim chcemy sie polaczyc
    wants_rating: HashMap<String, i32>, // dzielenie zadan (po dobraniu)

    // === lifecycle === //
    epoch: i32, // ktory mamy epoch/iteracje algorytmu (!to nie clock!)
    on_the_floor_now: i32, // ktos juz moze isc bo uzbieral zasoby
    send_once_floor: i32, // czy wyslalismy ze jestemy gotowi (tylko raz)
}

// wiadomosc transportowa (uproszczona)
#[derive(Default, Clone)]
pub struct Message {
    pub addr: i32,    // do kogo wysylamy (id: Peer)
    pub code: String, // typ komunikatu
    pub data: String, // zencodowana tresc wiadomosci
}

// wysyla wiadomosc do wszystkich (ograniczone uzycie)
pub fn broadcast(node: &Node, msg: Message) {
    for peer in node.peers.iter() {
        let mut msg_tmp = msg.clone();
        msg_tmp.addr = peer.nr;
        send(node, msg_tmp);
    }
}

// mechanizm wysylania wiadomosci odpowiednim kanalem
pub fn send_raw(queue: &Queue, peers: &HashSet<Peer>, id: &Peer, msg: Message) {
    // najpierw trzeba znalesc komu wyslac
    let peer = find_peer(msg.addr, &peers);

    match peer {
        Some(peer) => {
            // dodajemy na kolejke - inny process sie tym zajmie
            queue.push(Package {
                nr: id.nr, // kto wysyla (czyli my)
                from_addr: addr_str(&id.ip, &id.port),
                to_nr: peer.nr, // do kogo
                // oraz jaki on ma adres rzeczywisty (czyli IP+port)
                to_addr: addr_str(&peer.ip, &peer.port),
                code: msg.code, // dane z wiadomosci
                data: msg.data, // tutaj opakowane
            });
        }
        None => {
            error!("(send_raw) nie istnieje kanal o takim `peer.nr`");
        }
    }
}

// podobne do `send_raw` ale dla broadcast-u
pub fn send(node: &Node, msg: Message) {
    let peer = find_peer(msg.addr, &node.peers);

    match peer {
        Some(peer) => {
            node.queue_send.push(Package {
                nr: node.id.nr,
                from_addr: addr_str(&node.id.ip, &node.id.port),
                to_nr: peer.nr,
                to_addr: addr_str(&peer.ip, &peer.port),
                code: msg.code,
                data: msg.data,
            });
        }
        None => {
            error!("(send    ) nie istnieje kanal o takim `peer.nr`");
        }
    }
}

impl Node {
    // inicjacja wartosci w wezle
    pub fn new() -> Node {
        Node {
            id: Peer {
                ip: "127.0.0.1".to_string(),
                port: 9000,
                nr: rand::thread_rng().gen::<i32>().checked_rem(1000).unwrap(),
                fails: 0,
            },
            queue_recv: Queue::new(),
            queue_send: Queue::new(),
            domains: Vec::new(),
            peers: HashSet::new(),
            resources: HashMap::new(),
            wants: HashMap::new(),
            pseudo_have: HashMap::new(),
            transfer_luck: rand::thread_rng().gen::<i32>(),
            sex: 0,
            paired_with: -1, // czyli bez pary
            pseudo_paired: -1,
            wants_rating: HashMap::new(),
            on_the_floor_now: 0,
            epoch: 0,
            send_once_floor: 0,
        }
    }

    // ustawienie plci
    pub fn sex(&mut self, sex: i32) {
        self.sex = sex;
    }

    // ustawienie port-u
    pub fn port(&mut self, port: i32) {
        self.id.port = port;
    }

    // dodanie nowej sieci
    pub fn add(&mut self, domain: Domain) {
        self.domains.push(domain);
    }

    // odpalenie warstwy transportowej (async)
    pub fn start(&mut self) {
        // wiecej do wysylania
        for _ in 0..10 {
            let id1 = self.id.clone();
            let queue_send_thread = self.queue_send.clone();
            Node::thread_send(queue_send_thread, id1);
        }

        // niz do odbioru
        let id2 = self.id.clone();
        let queue_recv_thread = self.queue_recv.clone();
        Node::thread_recv(queue_recv_thread, id2);

        // glowna czesc
        // pojedynczy PROCES
        self.routine();
    }

    // watek wysylania z kolejek
    pub fn thread_send(queue_send_thread: Queue, id: Peer) {
        thread::Builder::new()
            .name("thread_send".to_string())
            .spawn(move || {
                worker_send(&queue_send_thread, &id);
            });
    }

    // watek na odbior z kolejek
    pub fn thread_recv(queue_recv_thread: Queue, id: Peer) {
        let (tx, rx) = mpsc::channel();
        thread::Builder::new()
            .name("thread_recv".to_string())
            .spawn(move || {
                worker_recv(tx, queue_recv_thread, id);
            });
        let srv = rx.recv().unwrap();
    }

    fn routine(&mut self) {
        let sleep_time = time::Duration::from_millis(200);

        // ile razy tanczyli (sekcja DANCE)
        let mut resting_count = 0;

        // inicjalizujemy poczatkowe zasoby (kazdy ma 2 masci + 5 warzyw)
        resource::init(self.id.nr, &mut self.resources, self.transfer_luck);

        // ile zasobow potrzebuja aby tanczyc
        self.wants = hashmap!(
            "masc".to_string() => 3,
            "warzywa 1kg".to_string() => 7
        );

        // chwilowa kopia (gdy sie juz podziela)
        let copy_wants = do_clone(&self.wants);

        // bedziemy zapisywac kiedy ostatnio proces tanczyl
        let start = SystemTime::now();
        let mut since_the_epoch = start
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards");

        loop {
            // (SCAN) co powien czas robimy scan sieci na nowe procesy
            if self.epoch % 50 == 0 || self.epoch == 0 {
                scan(&self.domains, &mut self.peers, &self.id);
            }

            println!("\n--- epoch={} ---\n", self.epoch);
            println!(
                "id.nr=\x1b[0;31m{}\x1b[0m | queue_recv({}) queue_send({})",
                self.id.nr,
                self.queue_recv.len(),
                self.queue_send.len()
            );

            ////////////////////////////////////////////////////////////////////

            // (FUZZY SHARE) co powien czas wysylamy nasze zasoby do kolegow
            if self.epoch % 10 == 0 {
                resource::spread(&self);
            }

            // (MESSAGE INTERPRETATION)
            while self.queue_recv.len() > 0 {
                let packet = self.queue_recv.pull();
                match packet {
                    Some(packet) => {
                        // gdy chodzi o zasoby
                        if packet.code.starts_with("resource") {
                            self.react_resource(packet);
                        // gdy chodzi o dobieranie sie w pary
                        } else if packet.code.starts_with("pair") {
                            self.react_pair(packet);
                        } else {
                            // FIXME: pozostale akcje?
                        }
                    }
                    None => warn!("ten pakiet juz nie istnieje w `queue_recv`"),
                }
            }

            // aktualny czas aby wyliczyc roznice
            let start = SystemTime::now();
            let current_the_epoch = start
                .duration_since(UNIX_EPOCH)
                .expect("Time went backwards");

            // (SYNC-DANCE) informujemy czlonka pary ze jestemy gotowi
            if self.send_once_floor == 0
                && self.resource_want()
                && !self.pair_want()
            /*  && (current_the_epoch
            .as_millis()
            .wrapping_sub(since_the_epoch.as_millis())
            > 3000)  */
            {
                let pair_msg = PairMessage {
                    owner_sex: self.sex,
                    owner: self.id.nr,
                    collecting_resources: do_clone(&self.wants_rating),
                };
                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: self.paired_with,
                        code: "pair-OK-DANCE-start".to_string(),
                        data: serde_json::to_string(&pair_msg)
                            .unwrap()
                            .to_string(),
                    },
                );
                self.send_once_floor = 1;
            }

            // (DANCE) tutaj odbywa sie taniec
            if self.on_the_floor_now == 1
                && self.resource_want()
                && !self.pair_want()
            {
                println!("\x1b[0;31m DANCING {:?} <-> {:?} \x1b[0m", self.id.nr, self.paired_with);
                let ten_millis = time::Duration::from_millis(
                    2000 + rand::thread_rng().gen::<u64>() % 3000,
                );
                thread::sleep(ten_millis);

                self.transfer_luck = rand::thread_rng().gen::<i32>();

                for (_, val) in self.resources.iter_mut() {
                    if val.owner == self.id.nr && val.status == "red" {
                        val.status = "green".to_string();
                        val.transfer_luck = self.transfer_luck;
                        val.transfer_with = -1;
                        val.time += 1;
                        val.epoch = self.epoch;
                    }
                }

                self.on_the_floor_now = 0;
                self.send_once_floor = 0;
                self.paired_with = -1;

                self.wants = do_clone(&copy_wants);
                self.stop_dancing();

                let start = SystemTime::now();
                since_the_epoch = start
                    .duration_since(UNIX_EPOCH)
                    .expect("Time went backwards");

                println!("\x1b[0;31m DANCING (out) \x1b[0m");

                resting_count += 1;

                // self.queue_recv.clear();
                // self.queue_send.clear();
            }

            // (STILL-GDY-GLOD) polepszanie zdolnosci zlodzieja (anneling?)
            if !self.resource_want() && self.epoch % 2 == 0 {
                // curve: 1.5-1000e^-log(MILLIS)

                /*let magic = current_the_epoch
                    .as_millis()
                    .wrapping_sub(since_the_epoch.as_millis())
                    as f64;
                let base = rand::thread_rng().gen::<i32>() as f64;
                let luck = (base * (1.5 - 500.0 * (-magic.ln()).exp())) as i32;*/

                let magic = current_the_epoch
                    .as_millis()
                    .wrapping_sub(since_the_epoch.as_millis());
                let luck = rand::thread_rng().gen::<i32>().abs();
                self.transfer_luck = cmp::max(
                    Wrapping(luck).0,
                    (Wrapping(self.transfer_luck)
                        + Wrapping(
                            (magic as i32).abs().checked_rem(1000).unwrap(),
                        ))
                    .0,
                );
            }

            // (CLEAN) odpady po wyjsciu z tanca
            for (_, val) in self.resources.iter_mut() {
                if (val.transfer_with != -1 && val.status == "green")
                {
                    val.transfer_with = -1;
                    val.status = "green".to_string();
                }
            }

            // (ZASOBY-DOWN) z czasem spada wartosc aby latwiej ukrasc
            for (_, val) in self.resources.iter_mut() {
                if val.owner == self.id.nr {
                    val.transfer_luck = cmp::max(val.transfer_luck, 0);
                    val.transfer_luck -= (self.transfer_luck / 10000) as i32;
                }
            }

            // (PSEUDO-HAVE) co powien czas warto uaktualnic swoja taktyke
            if self.epoch % 20 == 0 {
                for (key, val) in self.wants.iter() {
                    *self.pseudo_have.entry(key.to_string()).or_insert(0) = 0;
                }
            }

            ////////////////////////////////////////////////////////////////////
            let local_map: HashMap<String, i32> = self.resource_diff_strict();
            println!("\n\n\n{:#?}\n\n\n", local_map);
            let local_map2: HashMap<String, i32> = self.resource_diff();
            println!("\n\n\n{:#?}\n\n\n", local_map2);

            self.show_resources();
            println!("---------> {:#?} <---------", self.wants_rating);
            println!("(wants)==> {:#?} <=========", self.wants);
            println!(
                "PAIRING({}[{}] | {} | {})",
                self.id.nr, self.sex, self.pseudo_paired, self.paired_with
            );
            let f1 = self.on_the_floor_now;
            let f2 = self.resource_want();
            let f3 = self.pair_want();
            println!("on_the_floor_now={:#?} | resource_want={:#?} | pair_want={:#?}", f1, f2, f3);
            println!("resting_count ------------------> {}", resting_count);
            ////////////////////////////////////////////////////////////////////

            thread::sleep(sleep_time);
            self.epoch += 1;
        }
    }

    // resource ktore NAPRAWDE MAMY
    pub fn resource_diff(&mut self) -> HashMap<String, i32> {
        let mut local_map: HashMap<String, i32> = HashMap::new();
        for (key, val) in self.pseudo_have.iter() {
            *local_map.entry(key.to_string()).or_insert(0) += val;
        }
        for (_, val) in self.resources.iter() {
            if val.owner == self.id.nr && val.status == "red" {
                let key_want = val.code.to_string();
                *local_map.entry(key_want).or_insert(0) += 1;
            }
        }
        local_map
    }

    // resource jakie zdaja sie nam ze BEDZIEMY MIELI
    // (aby nie wysylac nie potrzebnych zapytan do serwera)
    pub fn resource_diff_strict(&mut self) -> HashMap<String, i32> {
        let mut local_map: HashMap<String, i32> = HashMap::new();
        for (_, val) in self.resources.iter() {
            if val.owner == self.id.nr && val.status == "red" {
                let key_want = val.code.to_string();
                *local_map.entry(key_want).or_insert(0) += 1;
            }
        }
        local_map
    }

    // do debugu
    pub fn show_resources(&mut self) {
        let mut tmp_vec: Vec<_> = self.resources.iter().collect();
        tmp_vec.sort_by(|(_, a), (_, b)| a.token.cmp(&b.token));

        for (_key, val) in tmp_vec {
            let mut status_pretty = val.status.clone();
            match status_pretty.as_str() {
                "green" => {
                    status_pretty =
                        format!("\x1b[0;32m{}\x1b[0m", status_pretty)
                }
                "red" => {
                    status_pretty =
                        format!("\x1b[0;31m{}\x1b[0m", status_pretty)
                }
                _ => status_pretty = status_pretty,
            }

            let mut our: String = val.owner.clone().to_string();
            if our == self.id.nr.to_string() {
                our = format!("\x1b[0;34m{}\x1b[0m", our)
            }

            println!(
                "RESOURCE({}): `{:12}` |{:10}| owner={:3} | status={:8} | {} | {} | {:10}",
                self.id.nr, val.code, val.token, our, status_pretty, val.transfer_with, val.time, val.transfer_luck
            );
        }
        println!("OUR LUCK = {}", self.transfer_luck);
    }

    // (TAKTYKA) policzmy co chcemy
    pub fn resource_want(&mut self) -> bool {
        let f1 = self.pair_want();
        let local_map: HashMap<String, i32> = self.resource_diff_strict();
        let mut diff: i32 = 0;
        for (key, val) in self.wants.iter() {
            let cur_diff = val - local_map.get(key).unwrap_or(&0);
            println!("----|||| `{}` |||| val={} | diff={}", key, val, cur_diff);

            // jesli czegosc nie mamy pytamy innych
            if cur_diff > 0 {
                for (_key2, val2) in self.resources.iter_mut() {
                    // ten warunek jest bardzo wazny
                    // bo nie chcemy powtarzac zapytan
                    // lub pytac transportowane zasoby
                    if val2.code == *key
                        && !f1
                        && val2.transfer_with == -1
                        && (val2.status == "green"
                            || (val2.status == "red"
                                && val2.owner != self.id.nr))
                    {
                        let mut tmp_val: Resource = val2.clone();
                        tmp_val.transfer_luck = self.transfer_luck;
                        tmp_val.transfer_with = self.id.nr;
                        // lokalne zmiany?
                        val2.transfer_with = self.id.nr;
                        val2.status = "q".to_string();
                        val2.epoch = self.epoch;
                        send_raw(
                            &self.queue_send,
                            &self.peers,
                            &self.id,
                            Message {
                                addr: tmp_val.owner,
                                code: "resource-want".to_string(),
                                data: serde_json::to_string(&tmp_val)
                                    .unwrap()
                                    .to_string(),
                            },
                        );
                        println!(
                            "__________________________ I AM IN {}",
                            tmp_val.owner
                        );
                    }
                }
            }

            diff += cur_diff;
        }
        diff <= 0
    }

    pub fn react_resource(&mut self, package: Package) {
        let fuzzy_resource: Resource =
            serde_json::from_str(&package.data).unwrap();
        let key = fuzzy_resource.token.to_string();

        // ktos wysyla nam info co ma i co sie dzieje
        if package.code == "resource-info" {
            if !self.resources.contains_key(&key) {
                println!(
                    "({}) something new! \x1b[0;35m{}\x1b[0m",
                    self.resources.len(),
                    key
                );
                self.resources.insert(key, fuzzy_resource);
            } else if self.resources[&key].owner == self.id.nr {
                // jesli jestesmy wlasciciela to lepiej wiemy
                return;
            } else if fuzzy_resource.time > self.resources[&key].time
                || (fuzzy_resource.time == self.resources[&key].time
                    && (fuzzy_resource.status == "red" || fuzzy_resource.status == "green")
                    && self.resources[&key].transfer_with == -1
                    && fuzzy_resource.owner == package.nr)
            {
                // albo pakiet jest bardziej aktualny
                // albo pakiet zostal zaktualizowany przez wlasciciela
                // I TO ON NAM WYSYLA (redirecty moga byc juz nie aktualne)
                println!("\x1b[0;33mUPDATED!!!!!!!!!!!!!!!!!! {}\x1b[0m", key);
                self.resources.insert(key, fuzzy_resource);
            }
            return;
        }

        let local_map: HashMap<String, i32> = self.resource_diff();
        let local_map_strict: HashMap<String, i32> =
            self.resource_diff_strict();
        let local_resource: &mut Resource =
            self.resources.get_mut(&key).unwrap();

        // FORMA ROZGRYWKI (kto ma wieksza liczbe)
        let A: i32 = local_resource.transfer_luck; // nasza liczba
        let B: i32 = fuzzy_resource.transfer_luck; // challanger

        // gdy byl zastuj w kanalach i mamy cos nie aktualnego
        if local_resource.time > fuzzy_resource.time {
            // gdy jestesmy w stanie wyslac prawidlowa odpowiedz
            if package.code == "resource-want" {
                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: package.nr,
                        code: "resource-rollback-req".to_string(),
                        data: serde_json::to_string(&local_resource)
                            .unwrap()
                            .to_string(),
                    },
                );
            } else {
                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: package.nr,
                        code: "resource-rollback-src".to_string(),
                        data: serde_json::to_string(&local_resource)
                            .unwrap()
                            .to_string(),
                    },
                );
            }
            return;
        }

        if package.code == "resource-want" {
            println!("\x1b[0;35mKOTWICA 1 (resource-want)\x1b[0m");

            println!(
                "[[[[[[[{}:{}]]]] {} < {}, {}",
                local_resource.status,
                local_resource.token,
                A,
                B,
                A < B
            );

            if (local_resource.transfer_with == -1
                || fuzzy_resource.transfer_with == self.id.nr)
                && local_resource.owner == self.id.nr
                && ((fuzzy_resource.transfer_with == self.id.nr
                    && local_resource.status == "q")
                    || local_resource.status == "green"
                    || ((self.wants.get(&fuzzy_resource.code).unwrap_or(&0)
                        - local_map_strict
                            .get(&fuzzy_resource.code)
                            .unwrap_or(&0)
                        != 0)
                        && local_resource.status == "red"
                        && A <= B))
            {
                println!("\t\t \x1b[0;32m--> ACCEPTED\x1b[0m");
                if local_resource.status == "red" {
                    println!("\x1b[0;33mSTILLING!!!!!!!!!!!!!!!!!!\x1b[0m");
                }
                local_resource.status = "waitfor".to_string();
                local_resource.transfer_with = fuzzy_resource.transfer_with;
                local_resource.transfer_luck = B;

                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: package.nr,
                        code: "resource-accept".to_string(),
                        data: serde_json::to_string(&local_resource).unwrap(),
                    },
                );
            } else {
                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: package.nr,
                        code: "resource-rollback-req".to_string(),
                        data: serde_json::to_string(&local_resource)
                            .unwrap()
                            .to_string(),
                    },
                );
                println!("\t\t \x1b[0;31m--> DECLINED l.transfer_with={} | l.owner={} self.id.nr={}\x1b[0m", local_resource.transfer_with, local_resource.owner, self.id.nr);
            }
            return;
        }

        if package.code == "resource-rollback-req"
            && local_resource.time <= fuzzy_resource.time
            && local_resource.owner != self.id.nr
        {
            println!(
                "\x1b[0;35mKOTWICA ROLL REQ (resource-rollback)\x1b[0m - anuluj"
            );
            local_resource.transfer_with = -1;
            local_resource.status = "green".to_string();
            return;
        }

        if package.code == "resource-rollback-src"
            && local_resource.time <= fuzzy_resource.time
        {
            println!("\x1b[0;35m ===========> UDALO2\x1b[0m - anuluj");
            local_resource.status = "green".to_string();
            local_resource.transfer_with = -1;
            local_resource.transfer_luck = self.transfer_luck / 2;
            return;
        }

        if package.code == "resource-accept" {
            println!("\x1b[0;35mKOTWICA 2 (resource-accept)\x1b[0m - czyli czy chce od niego");
            if self.wants.get(&fuzzy_resource.code).unwrap_or(&0)
                - local_map.get(&fuzzy_resource.code).unwrap_or(&0)
                > 0
                && (local_resource.transfer_with
                    == fuzzy_resource.transfer_with)
            {
                println!("\t\t \x1b[0;32m--> ACCEPTED\x1b[0m");
                *self.pseudo_have.entry(fuzzy_resource.code).or_insert(0) += 1;
                local_resource.status = "transfer".to_string();
                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: package.nr,
                        code: "resource-transfer".to_string(),
                        data: serde_json::to_string(&local_resource).unwrap(),
                    },
                );
            } else {
                println!(
                    "\x1b[0;34mMAMY JUZ WSZYSTKO2 {} {}\x1b[0m",
                    local_map.get(&key).unwrap_or(&0),
                    self.wants.get(&key).unwrap_or(&0)
                );
                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: package.nr,
                        code: "resource-rollback-src".to_string(),
                        data: serde_json::to_string(&local_resource).unwrap(),
                    },
                );

                println!("\t\t \x1b[0;31m--> DECLINED\x1b[0m");
                println!(
                    "\x1b[0;35mslow slow slwo ERRROEROEOROEOROREOEOREOEOOEROEOREROOREE\x1b[0m {} {} {} A={} B={} s {}", local_resource.status, local_resource.transfer_with, fuzzy_resource.owner, A, B, A < B);
            }
            return;
        }

        if package.code == "resource-transfer" {
            println!(
                "\x1b[0;35mKOTWICA 3 (resource-transfer)\x1b[0m {}",
                local_resource.token
            );

            if (local_resource.status == "transfer"
                && local_resource.owner == local_resource.transfer_with
                || local_resource.status == "waitfor")
                && local_resource.transfer_with == fuzzy_resource.transfer_with
                && local_resource.transfer_with != -1
            {
                println!(
                    "\t\t \x1b[0;32m--> ACCEPTED WUT={} FAT={}\x1b[0m",
                    local_resource.owner, local_resource.transfer_with
                );
                local_resource.owner = local_resource.transfer_with;
                local_resource.status = "-".to_string();
                local_resource.transfer_with = -2;

                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: package.nr,
                        code: "resource-done".to_string(),
                        data: serde_json::to_string(&local_resource).unwrap(),
                    },
                )
            } else {
                println!("\t\t \x1b[0;32m--> DECLINED\x1b[0m");
                println!(
                    "status={:?} local={:?} fuzzy={:?}",
                    local_resource.status,
                    local_resource.transfer_with,
                    fuzzy_resource.transfer_with
                );
                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: package.nr,
                        code: "resource-rollback-req".to_string(),
                        data: serde_json::to_string(&local_resource).unwrap(),
                    },
                );
            }
            return;
        }

        if package.code == "resource-done" {
            println!("\x1b[0;35mKOTWICA 4 (resource-done)\x1b[0m",);
            if self.id.nr == fuzzy_resource.owner {
                println!("\t\t \x1b[0;32m--> ACCEPTED\x1b[0m");
                local_resource.owner = self.id.nr;
                local_resource.transfer_with = -1;
                local_resource.transfer_luck = self.transfer_luck;
                local_resource.status = "red".to_string();
                local_resource.time += 1;

                *self
                    .pseudo_have
                    .entry(fuzzy_resource.code.clone())
                    .or_insert(0) -= 1;

                println!(
                    "==============> {:#?} ~~~~~~~~~~~~~~~~~~~~",
                    local_resource
                );

                let not_fuzzy_state =
                    serde_json::to_string(&local_resource).unwrap();
                broadcast(
                    self,
                    Message {
                        addr: -1,
                        code: "resource-info".to_string(),
                        data: not_fuzzy_state,
                    },
                );
            } else {
                *self
                    .pseudo_have
                    .entry(fuzzy_resource.code.clone())
                    .or_insert(0) -= 1;
                println!("\t\t \x1b[0;31m--> DECLINED\x1b[0m");
            }
            return;
        }
    }

    // Zwraca true jeśli wciąż potrzebuje pary
    pub fn pair_want(&mut self) -> bool {
        // jeśli nie ma pary
        if self.paired_with == -1 {
            // uzupełnij poszukiwane zasoby o losowa liczbe
            if self.wants_rating.is_empty() {
                for res in do_clone(&self.resources) {
                    let x = rand::thread_rng()
                        .gen::<i32>()
                        .checked_rem(1000)
                        .unwrap();
                    self.wants_rating.insert(res.1.code, x);
                }
            }

            // informuje o tym jakie wylosował liczby dla zasobów
            let pair_msg = PairMessage {
                owner_sex: self.sex,
                owner: self.id.nr,
                collecting_resources: do_clone(&self.wants_rating),
            };

            // Rozsyła request o parę do każdego innego procesu
            broadcast(
                self,
                Message {
                    addr: -1,
                    code: "pair-REQ-PAIR".to_string(),
                    data: serde_json::to_string(&pair_msg).unwrap(),
                },
            );

            // true jeśli wciąż szuka pary
            return self.paired_with == -1;
        }

        // już ma parę, wiec następnym razem bedzie od nowa przydzielał sobie resource
        self.wants_rating = HashMap::new();
        false
    }

    // reakcja na wiadomości o parze
    pub fn react_pair(&mut self, package: Package) {
        let received_message: PairMessage =
            serde_json::from_str(&package.data).unwrap();
        println!("\x1b[0;35m {} \x1b[0m", package.code);

        /*
        if self.pseudo_paired != -1 && self.paired_with == -1 && self.epoch % 30 == 0 {
                let pair_msg = PairMessage {
                    owner_sex: self.sex,
                    owner: self.id.nr,
                    collecting_resources: do_clone(&self.wants_rating),
                };

                // Poinformuj o gotowości do tańca
                send_raw(
                    &self.queue_send,
                    &self.peers,
                    &self.id,
                    Message {
                        addr: self.pseudo_paired,
                        code: "pair-READY-TO-DANCE".to_string(),
                        data: serde_json::to_string(&pair_msg).unwrap(),
                    },
                );
        }
        */

        // nie odbiera wiadomości od samego siebie
        if received_message.owner != self.id.nr {
            match package.code.as_str() {
                "pair-REQ-PAIR" => {
                    // jeżeli nie ma pary i process jest innej płci (nie dopuszczamy tańców jednopłciowych)
                    if self.paired_with == -1
                        && received_message.owner_sex != self.sex
                    {
                        let msg_to_send = PairMessage {
                            owner_sex: self.sex,
                            owner: self.id.nr,
                            collecting_resources: do_clone(&self.wants_rating),
                        };
                        // Odeślij wiadomość 'zatańcz ze mną'
                        send_raw(
                            &self.queue_send,
                            &self.peers,
                            &self.id,
                            Message {
                                addr: received_message.owner,
                                code: "pair-DANCE-WITH-ME".to_string(),
                                data: serde_json::to_string(&msg_to_send)
                                    .unwrap(),
                            },
                        );
                    }
                }
                "pair-DANCE-WITH-ME" => {
                    // jeżeli nie ma pary ani nie jest w trakcie potwierdzania pary
                    if self.paired_with == -1 && self.pseudo_paired == -1 {
                        let pair_msg = PairMessage {
                            owner_sex: self.sex,
                            owner: self.id.nr,
                            collecting_resources: do_clone(&self.wants_rating),
                        };

                        // Poinformuj o gotowości do tańca
                        send_raw(
                            &self.queue_send,
                            &self.peers,
                            &self.id,
                            Message {
                                addr: received_message.owner,
                                code: "pair-READY-TO-DANCE".to_string(),
                                data: serde_json::to_string(&pair_msg).unwrap(),
                            },
                        );

                        // zaznacz ze jest w trakcie potwierdzania pary
                        self.pseudo_paired = package.nr;
                    }
                }
                "pair-READY-TO-DANCE" => {
                    let pair_msg = PairMessage {
                        owner_sex: self.sex,
                        owner: self.id.nr,
                        collecting_resources: do_clone(&self.wants_rating),
                    };

                    for res in received_message.collecting_resources {
                        println!("\n\n\n\n\n\n\n----------------> {:#?}", res);
                        let self_res_rate =
                            self.wants_rating.get(&res.0).unwrap_or_else(|| &0);

                        if self_res_rate < &res.1
                            || (self_res_rate == &res.1
                                && self.sex < received_message.owner_sex)
                        {
                            *self.wants.get_mut(&res.0).unwrap() = 0;
                            let new_transfer_luck =
                                rand::thread_rng().gen::<i32>();
                            for (_, val) in self.resources.iter_mut() {
                                if val.owner == self.id.nr
                                    && val.code == res.0
                                    && val.transfer_with == -1
                                {
                                    println!(
                                        "REMOVE THAT!!!!!!!!!!!!!!!!!!!!!!!!!"
                                    );
                                    val.status = "green".to_string();
                                    val.transfer_luck = new_transfer_luck;
                                    val.transfer_with = -1;
                                    val.time += 10;
                                }
                            }
                        }
                    }

                    // jeżeli nie ma pary ani nie jest w trakcie potwierdzania pary
                    if self.paired_with == -1 && self.pseudo_paired == -1 {
                        // FIXME: tutaj sprawdzic? czy dziala?
                        // Wyślij taką samą wiadomość
                        send_raw(
                            &self.queue_send,
                            &self.peers,
                            &self.id,
                            Message {
                                addr: received_message.owner,
                                code: "pair-READY-TO-DANCE".to_string(),
                                data: serde_json::to_string(&pair_msg).unwrap(),
                            },
                        );
                        // Zaznacz że jesteś w trakcie zawierania pary
                        self.pseudo_paired = package.nr;
                    }
                    // jeżeli nie ma pary i jest w trakcie potwierdzania pary
                    else if self.paired_with == -1
                        && self.pseudo_paired == package.nr
                    {
                        // Wyślij potwierdzenie dobrania w parę
                        send_raw(
                            &self.queue_send,
                            &self.peers,
                            &self.id,
                            Message {
                                addr: received_message.owner,
                                code: "pair-OK-DANCE".to_string(),
                                data: serde_json::to_string(&pair_msg).unwrap(),
                            },
                        );
                        // Zaznacz że jesteś w parze
                        self.paired_with = received_message.owner;
                        self.pseudo_paired = -1;
                    }
                    // W innych przypadkach poinformuj że już za późno
                    else {
                        send_raw(
                            &self.queue_send,
                            &self.peers,
                            &self.id,
                            Message {
                                addr: received_message.owner,
                                code: "pair-TOO-LATE".to_string(),
                                data: serde_json::to_string(&pair_msg).unwrap(),
                            },
                        );
                    }
                }
                "pair-TOO-LATE" => {
                    // Zaznacz że proces z którym zawierałeś parę odrzucił
                    self.pseudo_paired = -1;
                }
                "pair-OK-DANCE" => {
                    // Zaznacz że jesteś w parze
                    self.paired_with = received_message.owner;
                    self.pseudo_paired = -1;
                }
                "pair-OK-DANCE-start" => {
                    self.on_the_floor_now = 1;
                }
                "pair-I-NEED-REST" => {
                    let pair_msg = PairMessage {
                        owner_sex: self.sex,
                        owner: self.id.nr,
                        collecting_resources: do_clone(&self.wants_rating),
                    };

                    // Poinformuj że zgadzasz się na przerwę
                    send_raw(
                        &self.queue_send,
                        &self.peers,
                        &self.id,
                        Message {
                            addr: self.paired_with,
                            code: "pair-OK-REST".to_string(),
                            data: serde_json::to_string(&pair_msg).unwrap(),
                        },
                    );

                    // Porzuć parę
                    self.paired_with = -1;
                    self.pseudo_paired = -1;

                    // Ponownie zaznacz że szukasz zasobów do tańca // FIXME jakoś to uogólnić, żeby w jednym miejscu sie deklarowało
                    self.wants = hashmap!("masc".to_string() => 3, "warzywa 1kg".to_string() => 7);
                }
                "pair-OK-REST" => {
                    // Porzuć parę
                    self.paired_with = -1;
                    self.pseudo_paired = -1;
                    // Ponownie zaznacz że szukasz zasobów do tańca // FIXME jakoś to uogólnić, żeby w jednym miejscu sie deklarowało
                    self.wants = hashmap!("masc".to_string() => 3, "warzywa 1kg".to_string() => 7);
                }
                _ => {}
            }
        }
    }

    pub fn stop_dancing(&mut self) {
        let pair_msg = PairMessage {
            owner_sex: self.sex,
            owner: self.id.nr,
            collecting_resources: do_clone(&self.wants_rating),
        };

        send_raw(
            &self.queue_send,
            &self.peers,
            &self.id,
            Message {
                addr: self.paired_with,
                code: "pair-I-NEED-REST".to_string(),
                data: serde_json::to_string(&pair_msg).unwrap(),
            },
        );
    }
}
