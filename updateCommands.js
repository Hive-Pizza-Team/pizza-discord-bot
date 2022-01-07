const fetch = require('node-fetch')
const dotenv = require('dotenv').config()

const apiEndpoint = process.env.COMMANDS_API_ENDPOINT
const botToken = process.env.DISCORD_TOKEN

const gifCommandData = {
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
}


const hkplayerCommandData = {
  "name": "hkplayer",
  "description": "Show HashKings player info.",
  "options": [{
    "type": 3,
    "name": "player",
    "description": "name of player",
    "required": true
  }]
}


async function main () {

  var response = await fetch(apiEndpoint, {
    method: 'get',
    headers: {
      'Authorization': 'Bot ' + botToken,
      'Content-Type': 'application/json'
    }
  })
  var json = await response.json()
  //console.log(response)
  console.log(json)

  response = await fetch(apiEndpoint, {
    method: 'post',
    body: JSON.stringify(gifCommandData),
    headers: {
      'Authorization': 'Bot ' + botToken,
      'Content-Type': 'application/json'
    }
  })
  json = await response.json()

  //console.log(response)
  console.log(json)

    response = await fetch(apiEndpoint, {
    method: 'post',
    body: JSON.stringify(hkplayerCommandData),
    headers: {
      'Authorization': 'Bot ' + botToken,
      'Content-Type': 'application/json'
    }
  })
  json = await response.json()

  //console.log(response)
  console.log(json)

  const rcCommandData = {
  "name": "rc",
  "description": "Show Hive resource credits status for wallet.",
  "options": [{
    "type": 3,
    "name": "wallet",
    "description": "name of wallet",
    "required": true
  }]
}

    response = await fetch(apiEndpoint, {
    method: 'post',
    body: JSON.stringify(rcCommandData),
    headers: {
      'Authorization': 'Bot ' + botToken,
      'Content-Type': 'application/json'
    }
  })
  json = await response.json()

  //console.log(response)
  console.log(json)

}
main()