// FIXME: zrobic do tego pliku przyjazne testy
// FIXME: wizualizacja struktury p2p w pythonie?

use indicatif::{ProgressBar, ProgressStyle};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::hash::Hash;
use std::hash::Hasher;
use std::io::prelude::*;
use std::io::ErrorKind::TimedOut;
use std::net::SocketAddr;
use std::net::TcpListener;
use std::net::TcpStream;
use std::sync::{Arc, RwLock};
use std::{thread, time};

#[derive(Default, Clone, Eq, Debug)]
pub struct Peer {
    pub ip: String,
    pub port: i32,
    pub nr: i32,
    pub fails: i32,
}

pub struct Domain {
    pub ip: String,
    pub lhs: i32,
    pub rhs: i32,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Package {
    pub nr: i32,
    pub from_addr: String,
    pub to_nr: i32,
    pub to_addr: String,
    pub code: String,
    pub data: String,
}

// FIXME: create something like NETWORK and MESSAGE?
//        and rewrite Node --> to something simpler

////////////////////////////////////////////////////////////////////////////////

pub fn addr_str(ip: &str, port: &i32) -> String {
    format!("{}:{}", ip, port)
}

impl Hash for Peer {
    fn hash<H>(&self, state: &mut H)
    where
        H: Hasher,
    {
        let blob_raw = addr_str(&self.ip, &self.port);
        let blob = blob_raw.as_bytes();
        state.write(&blob);
        state.finish();
    }
}

impl PartialEq for Peer {
    fn eq(&self, other: &Peer) -> bool {
        addr_str(&self.ip, &self.port) == addr_str(&other.ip, &other.port)
    }
}

////////////////////////////////////////////////////////////////////////////////

pub struct Queue {
    lock: Arc<RwLock<Vec<Package>>>,
    clone_num: i32,
}

impl Queue {
    pub fn new() -> Queue {
        Queue {
            lock: Arc::new(RwLock::new(Vec::new())),
            clone_num: 0,
        }
    }

    pub fn len(&self) -> usize {
        let vec = self.lock.read().unwrap();
        (*vec).len()
    }

    pub fn push(&self, package: Package) {
        let mut vec = self.lock.write().unwrap();
        (*vec).push(package)
    }

    pub fn pull(&self) -> Option<Package> {
        let mut vec = self.lock.write().unwrap();
        (*vec).pop()
    }

    pub fn clear(&self) {
        let mut vec = self.lock.write().unwrap();
        (*vec).retain(|x| false);
    }

    pub fn clone(&self) -> Queue {
        Queue {
            lock: self.lock.clone(),
            clone_num: self.clone_num + 1,
        }
    }
}

////////////////////////////////////////////////////////////////////////////////

pub fn find_peer(nr: i32, peers: &HashSet<Peer>) -> Option<Peer> {
    for x in peers.iter().cloned() {
        if x.nr == nr {
            return Some(x);
        }
    }
    None
}

////////////////////////////////////////////////////////////////////////////////

//use actix_web::{get, web, App, HttpRequest, HttpServer, Responder};

use std::process;
use std::sync::mpsc;

use actix_rt::System;
use actix_web::{dev::Server, middleware, web, App, HttpRequest, HttpServer, Responder};
use std::sync::Mutex;

struct NodeData {
    queue_recv: Queue,
    id: Peer
}

async fn index(req: HttpRequest, body: web::Bytes, data: web::Data<Mutex<NodeData>>) -> impl Responder {
    let mut data = data.lock().unwrap();
    let package: Package = serde_json::from_slice(&body).unwrap();

    if package.code == "SCAN" && package.data == "PING" {
        let resend_packet = Package {
                nr: data.id.nr,
                from_addr: addr_str(&data.id.ip, &data.id.port),
                to_nr: package.nr,
                to_addr: package.from_addr.clone(),
                code: "SCAN".to_string(),
                data: "PONG".to_string(),
            };
        println!("------------------< PING >------------------");
        return serde_json::to_string(&resend_packet).unwrap();
    }

    data.queue_recv.push(package);
    "ACCEPTED!".to_string()
}

//use hyper::{Client, Uri};
use std::io::{stdout, Write};
use futures::executor::block_on;
use curl::easy::Easy;

pub fn new_transmit(packet: Package) -> Result<Package, String> {
    let url: String = format!("http://{}/", packet.to_addr);
    let url_slice: &str = &url[..];

    let packet_r = serde_json::to_string(&packet).unwrap();
    let mut data = packet_r.as_bytes();

    let mut dst = Vec::new();
    let mut easy = Easy::new();
    easy.url(url_slice).unwrap();

    easy.post(true).unwrap();
    easy.post_field_size(data.len() as u64).unwrap();

    {
        let mut transfer = easy.transfer();
        transfer.read_function(|buf| {
            Ok(data.read(buf).unwrap_or(0))
        }).unwrap();
        transfer.write_function(|data| {
            dst.extend_from_slice(data);
            Ok(data.len())
        }).unwrap();

        transfer.perform();
    }

    let result = serde_json::from_slice(&dst);

    match result {
        Ok(result) => {
            let package: Package = result;
            return Ok(package);
        }
        Err(result) => Err("`stream` jest pusty".to_string()),
    }
}

pub fn transmit(
    packet: Package,
) -> Result<Package, String> {

    let new_packet = packet.clone();
    let result = new_transmit(new_packet);

    //thread::sleep(time::Duration::from_secs(50));

    match result {
        Ok(result) => {
            return Ok(result);
        }
        Err(result) => Err("`stream` jest pusty".to_string()),
    }

    /*
    //process::exit(1);
    //block_on(future);

    //////////////////////////////////////////////////////////
    let timeout_time = time::Duration::from_millis(3000);
    let stream2 = match stream {
        Some(stream) => Ok(stream),
        None => {
            let addr = addr.unwrap();
            TcpStream::connect_timeout(&addr, timeout_time)
        }
    };

    match stream2 {
        Ok(stream) => {
            let packet_r = serde_json::to_string(&packet).unwrap();
            let mut stream = stream;
            stream
                .write_all(packet_r.as_bytes())
                .expect("nie moge wyslac pakietu bo nie dziala `stream`");
            print!("+");
            Ok(stream)
        }
        Err(error) => Err(error),
    }*/
}

use std::io::BufReader;
pub fn getout(stream: &TcpStream) -> Result<Package, String> {
    let bufsize = 1024;
    let mut buf = vec![0u8; bufsize];
    let mut stream = stream;
    let result = stream.read(&mut buf);
    /*for header in BufReader::new(&mut stream).lines() {
        let header = header.unwrap();
        if header == "\0" { break }
    }*/
    match result {
        Ok(result) => {
            let buftext = String::from_utf8_lossy(&buf);
            let bufres = buftext.trim_matches(char::from(0));
            if bufres.chars().count() < 2 {
                return Err("`stream` jest pusty".to_string());
            }
            let packet: Package = serde_json::from_str(&bufres).unwrap();
            return Ok(packet);
        }
        Err(result) => Err("`stream` jest pusty".to_string()),
    }
}

////////////////////////////////////////////////////////////////////////////////

// https://github.com/actix/examples/blob/master/run-in-thread/src/main.rs


pub fn worker_recv(tx: mpsc::Sender<Server>, queue_recv: Queue, id: Peer) -> std::io::Result<()> {
    println!("==> SERVER {}", id.port);

    let localhost = "127.0.0.1";

    let mut sys = System::new("test");

    let data = web::Data::new(Mutex::new(NodeData{ queue_recv: queue_recv, id: id.clone() }));

    // process::exit(1);
    let srv = HttpServer::new(move ||
            App::new()
            .app_data(data.clone())
            .service(web::resource("/").to(index))
        )
        .bind(addr_str(&localhost.to_string(), &id.port))
        .expect("Can not bind!")
        .run();

    // send server controller to main thread
    let _ = tx.send(srv.clone());

    // run future
    sys.block_on(srv)
}

pub fn worker_send(queue_send: &Queue, _id: &Peer) {
    let sleep_time = time::Duration::from_millis(10);
    // FIXME: sprytny dobor tego timeout? na bazie ilosci
    //        sredniej ilosci len() przy iteracjach
    loop {
        while queue_send.len() > 0 {
            if queue_send.len() > 1000 {
                // FIXME: clear queue
            }
            let packet = queue_send.pull();
            match packet {
                Some(packet) => {
                    transmit(packet);
                }
                None => warn!("ten pakiet juz nie istnieje w `queue_send`"),
            }
        }
        thread::sleep(sleep_time);
    }
}

////////////////////////////////////////////////////////////////////////////////

pub fn scan<S: std::hash::BuildHasher>(
    domains: &[Domain],
    peers: &mut HashSet<Peer, S>,
    id: &Peer,
) {
    let timeout_tries = 25;
    let progressfmt = "{spinner:.green} [{elapsed_precise}] \
                       [{bar:40.cyan/blue}] {pos:>7}/{len:7} ({eta}) {msg}";

    println!("!!!SCAN!!!");

    for domain in domains.iter() {
        info!("sprawdzam {}:{}-{}", domain.ip, domain.lhs, domain.rhs);

        let pb = ProgressBar::new((domain.rhs - domain.lhs) as u64);
        pb.set_style(
            ProgressStyle::default_bar()
                .template(progressfmt)
                .progress_chars("1>0"),
        );

        'each_port: for port in domain.lhs..=domain.rhs {
            pb.inc(1);

            let addr_raw = addr_str(&domain.ip, &port);

            let result = transmit(
                Package {
                    nr: id.nr,
                    from_addr: addr_str(&id.ip, &id.port),
                    to_nr: -1,
                    to_addr: addr_raw,
                    code: "SCAN".to_string(),
                    data: "PING".to_string(),
                },
            );

            match result {
                Ok(package) => {
                        peers.replace(Peer {
                            ip: domain.ip.to_owned(),
                            port: port,
                            nr: package.nr,
                            fails: 0,
                        });
                }
                Err(error) => {
                    info!("{:?}", error);
                }
            }
        }

        pb.finish_with_message(&domain.ip.to_string());
    }

    peers.retain(|k| k.fails < timeout_tries);

    let seq: Vec<Peer> = peers.iter().cloned().collect();
    for mut x in seq {
        x.fails += 1;
        peers.replace(x);
    }
}
