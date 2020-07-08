#[macro_use]
extern crate log;
extern crate pooldance;

use pooldance::{network::Domain, node::Node};
use std::{env, thread};
use rand::{Rng};

// FIXME: czyszczenie poprzednich procesow
// ps -ef | grep 'pooldance' | grep -v grep | awk '{print $2}' | xargs -r kill -9

pub fn main() {
    env_logger::init();

    // FIXME: informacja z helpem? (jakie argumenty)

    let mut port_lhs = 9000;
    let mut port_rhs = port_lhs;
    let mut sex = rand::thread_rng().gen::<i32>().abs().checked_rem(2).unwrap();

    let args: Vec<_> = env::args().collect();
    if args.len() == 2 {
        port_lhs = args[1].parse().unwrap();
        port_rhs = port_lhs;
        info!("ustawiam port={}", port_lhs);
    } else if args.len() == 3 {
        port_lhs = args[1].parse().unwrap();
        port_rhs = args[2].parse().unwrap();
        info!("ustawiam port={}..{}", port_lhs, port_rhs);
    }
    else if args.len() == 4 {
        port_lhs = args[1].parse().unwrap();
        port_rhs = args[2].parse().unwrap();
        // Płeć jako int żeby być poprawnym politycznie
        sex = args[3].parse().unwrap();
        info!("ustawiam port={}..{} i płeć {}", port_lhs, port_rhs, sex);
    }

    let mut childs = Vec::new();

    for port in port_lhs..=port_rhs {
        childs.push(
            thread::Builder::new().name(format!("node_{}", port)).spawn(
                move || {
                    let mut node: Node = Node::new();
                    node.port(port);
                    node.sex(sex);

                    // FIXME: czytanie konfiguracji z pliku?
                    node.add(Domain {
                        ip: "127.0.0.1".to_string(),
                        lhs: 9000,
                        rhs: 9030,
                    });

                    node.add(Domain {
                        ip: "27947a5d5d91.ngrok.io".to_string(),
                        lhs: 80,
                        rhs: 80,
                    });

                    node.start();
                },
            ),
        );
    }

    for child in childs {
        println!("----> {:?}", child);
        child.unwrap().join();
    }
}
