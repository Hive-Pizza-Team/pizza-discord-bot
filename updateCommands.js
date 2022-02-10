const fetch = require('node-fetch')
const dotenv = require('dotenv').config()
const sleep = require('sleep-promise');

const apiEndpoint = process.env.COMMANDS_API_ENDPOINT
const botToken = process.env.DISCORD_TOKEN

var allCommandData = [
/*{
  "name": "gif",
  "description": "Show a gif!",
  "options": [{
    "type": 3,
    "name": "category",
    "description": "name of a gif category",
    "required": false,
    "choices": [
      {"name": "pizza", value: "pizza"},
      {"name": "pineapple", value: "pineapple"},
      {"name": "beard", value: "beard"},
      {"name": "huzzah", value: "huzzah"},
      {"name": "bro", value: "bro"},
      {"name": "risingstar", value: "risingstar"},
      {"name": "stickup", value: "stickup"},
      {"name": "oneup", value: "oneup"},
      {"name": "dibblers", value: "dibblers"}
    ]
  }]
},
{
  "name": "hkplayer",
  "description": "Show HashKings player info.",
  "options": [{
    "type": 3,
    "name": "player",
    "description": "name of player",
    "required": true
  }]
},
{
  "name": "prefix",
  "description": "Admin-only - print and change bot's command prefix.",
  "options": [{
    "type": 3,
    "name": "newprefix",
    "description": "new prefix to set",
    "required": false
  }]
},
{
  "name": "rc",
  "description": "Show Hive resource credits status for wallet.",
  "options": [{
    "type": 3,
    "name": "wallet",
    "description": "name of wallet",
    "required": true
  }]
},
{
  "name": "witness",
  "description": "Print Hive Witness Info.",
  "options": [{
    "type": 3,
    "name": "witnessname",
    "description": "name of witness",
    "required": false
  }]
},
{
  "name": "hewitness",
  "description": "Print Hive-Engine Witness Info.",
  "options": [{
    "type": 3,
    "name": "witnessname",
    "description": "name of witness",
    "required": false
  }]
},
{
  "name": "dluxnodes",
  "description": "Check DLUX Nodes Status."
},
{
  "name": "sellbook",
  "description": "Check Hive-Engine sell book for token.",
  "options": [{
    "type": 3,
    "name": "symbol",
    "description": "Hive-Engine token symbol. i.e. PIZZA.",
    "required": false
  }]
},
{
  "name": "buybook",
  "description": "Check Hive-Engine buy book for token.",
  "options": [{
    "type": 3,
    "name": "symbol",
    "description": "Hive-Engine token symbol. i.e. PIZZA.",
    "required": false
  }]
},
{
  "name": "top10",
  "description": "Print Hive-Engine token rich list top 10.",
  "options": [{
    "type": 3,
    "name": "symbol",
    "description": "Hive-Engine token symbol. i.e. PIZZA.",
    "required": false
  }]
},
{
  "name": "tokenomics",
  "description": "Print Hive-Engine token distribution info.",
  "options": [{
    "type": 3,
    "name": "symbol",
    "description": "Hive-Engine token symbol. i.e. PIZZA.",
    "required": false
  }]
},
{
  "name": "price",
  "description": "Print Hive-Engine / CoinGecko market price info.",
  "options": [{
    "type": 3,
    "name": "symbol",
    "description": "Hive-Engine token symbol. i.e. PIZZA.",
    "required": false
  }]
},
{
  "name": "history",
  "description": "Print Hive-Engine market trade history.",
  "options": [{
    "type": 3,
    "name": "symbol",
    "description": "Hive-Engine token symbol. i.e. PIZZA.",
    "required": false
  }]
},
{
  "name": "blog",
  "description": "Link to latest post from blog.",
  "options": [{
    "type": 3,
    "name": "name",
    "description": "Hive blog name, i.e. hive.pizza.",
    "required": true
  }]
},
{
  "name": "bal",
  "description": "Print Hive-Engine wallet balances.",
  "options": [{
    "type": 3,
    "name": "wallet",
    "description": "Hive wallet name, i.e. hive.pizza.",
    "required": true
  },{
    "type": 3,
    "name": "symbol",
    "description": "Hive-Engine token symbol, i.e. PIZZA.",
    "required": false
  }]
},
{
  "name": "bals",
  "description": "Print Hive-Engine wallet balances.",
  "options": [{
    "type": 3,
    "name": "wallet",
    "description": "Hive wallet name, i.e. hive.pizza.",
    "required": true
  }]
},
{
  "name": "info",
  "description": "Print Hive.Pizza project link."
},
{
  "name": "links",
  "description": "Use these links to support Hive.Pizza."
},
{
  "name": "pools",
  "description": "Check Hive-Engine DIESEL Pool Balances for Wallet.",
  "options": [{
    "type": 3,
    "name": "wallet",
    "description": "Hive wallet name, i.e. hive.pizza.",
    "required": true
  }]
},
{
  "name": "pool",
  "description": "Check Hive-Engine DIESEL Pool Info.",
  "options": [{
    "type": 3,
    "name": "pool",
    "description": "DIESEL Pool symbol pair, i.e. SWAP.HIVE:PIZZA",
    "required": false
  }]
},
{
  "name": "poolrewards",
  "description": "Check Hive-Engine DIESEL Pool Rewards Info.",
  "options": [{
    "type": 3,
    "name": "pool",
    "description": "DIESEL Pool symbol pair, i.e. SWAP.HIVE:PIZZA",
    "required": false
  }]
},
{
  "name": "exodecards",
  "description": "Get a player's Exode card collection info.",
  "options": [{
    "type": 3,
    "name": "player",
    "description": "Name of player, i.e. thebeardflex.",
    "required": true
  }]
},
{
  "name": "apr",
  "description": "Calculate approx. APR for HP delegation.",
  "options": [{
    "type": 3,
    "name": "delegation_amount",
    "description": "Amount of HP delegated.",
    "required": true
  },{
    "type": 3,
    "name": "poolsize",
    "description": "Size of daily rewards pool.",
    "required": false
  }]
},
{
  "name": "rsplayer",
  "description": "Check Rising Star Player Stats.",
  "options": [{
    "type": 3,
    "name": "player",
    "description": "Name of player, i.e. thebeardflex.",
    "required": true
  }]
},
{
  "name": "status",
  "description": "Print bot's status information."
},
{
  "name": "sl",
  "description": "Fetch Splinterlands info for player or PIZZA guilds.",
  "options": [{
    "type": 3,
    "name": "subcommand",
    "description": "player, guild, brawl",
    "required": true
  },{
    "type": 3,
    "name": "arg",
    "description": "Name of player, status, timer.",
    "required": true
  }]
},*/
{
  "name": "search",
  "description": "Search for Hive content.",
  "options": [{
    "type": 3,
    "name": "query",
    "description": "Search query",
    "required": true
  },{
    "type": 3,
    "name": "sort",
    "description": "How to filter search results.",
    "required": false,
    "choices": [
      {"name": "newest", value: "neweset"},
      {"name": "relevance", value: "relevance"}
    ]
  }]
}
]


async function main () {

  /*var response = await fetch(apiEndpoint, {
    method: 'get',
    headers: {
      'Authorization': 'Bot ' + botToken,
      'Content-Type': 'application/json'
    }
  })
  var json = await response.json()
  //console.log(response)
  console.log(json)*/

  for (let offset in allCommandData) {
      response = await fetch(apiEndpoint, {
      method: 'post',
      body: JSON.stringify(allCommandData[offset]),
      headers: {
        'Authorization': 'Bot ' + botToken,
        'Content-Type': 'application/json'
      }
    })
    json = await response.json()

    //console.log(response)
    console.log(json)
    await sleep(4000); // Wait 4000 ms
  }
}
main()