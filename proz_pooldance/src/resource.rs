use crate::node::{broadcast, Message, Node};
use rand::Rng;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Resource {
    pub code: String,
    pub token: i32,
    pub owner: i32,
    pub status: String,
    pub transfer_with: i32,
    pub transfer_luck: i32,
    pub time: i32,
    pub epoch: i32,
    // time out if not resting
    // stilling if timeout
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct PairMessage {
    pub owner_sex: i32,
    pub owner: i32,
    pub collecting_resources: HashMap<String, i32>,
}

pub fn init(
    nr: i32,
    resources: &mut HashMap<String, Resource>,
    transfer_luck: i32,
) {
    println!("HELLO FROM INIT!");

    for _ in 0..2 {
        let idx: i32 =
            (nr * 100_000) + (rand::thread_rng().gen::<i32>() % 1000).abs();
        resources.insert(
            idx.to_string(),
            Resource {
                token: idx,
                owner: nr,
                code: "masc".to_string(),
                status: "green".to_string(),
                transfer_with: -1, // # FIXME: nie ujemne wartosci node-ow
                transfer_luck,
                time: 0,
                epoch: 0,
            },
        );
    }

    for _ in 0..5 {
        let idx: i32 =
            (nr * 100_000) + (rand::thread_rng().gen::<i32>() % 1000).abs();
        resources.insert(
            idx.to_string(),
            Resource {
                token: idx,
                owner: nr,
                code: "warzywa 1kg".to_string(),
                status: "green".to_string(),
                transfer_with: -1, // # FIXME: nie ujemne wartosci node-ow
                transfer_luck,
                time: 0,
                epoch: 0,
            },
        );
    }
}

pub fn spread(node: &Node) {
    for (_key, val) in node.resources.iter() {
        /*if val.owner != node.id.nr {
            continue;
        }*/
        let val2 = val.clone();
        let resource_r = serde_json::to_string(&val2).unwrap();
        broadcast(
            node,
            Message {
                addr: node.id.nr,
                code: "resource-info".to_string(),
                data: resource_r.to_string(),
            },
        );
    }
}
