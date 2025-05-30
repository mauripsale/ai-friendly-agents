Self: https://github.com/palladius/ai-friendly-agents/

## Agents

My friendly agents:

* 🟢 **Alfred Pennyless** 🦇 (Concierge, able to call other agents). Currently supports (and tested with): Claudia, Larry, Serpeverde, Siculo, Trixie, Vicky.
* 🟢 **Claudia Gugghelheim** ☁️ (Google Cloud agent). Inspired by Cloud: 🔴🔵🟢🟡
* 🟢 **Codie Smulders** 🐍 (code agent). For now, just `built_in_code_execution` from ADK.
* 🟢 **Larry** 🧢  (cURLer / Google). For the moment, just googling 🔎 is implemented.
* 🟢 **Serpeverde** 🧙 (SERP API Executor, basically a Google Search wrapper). For now supports **Maps** 🌍 , **Flights** ✈️ and **Hotels** 🏨 .
  Coming soon: Search 🔎 (for the moment, ask Larry :P)
* 🟢 **Salvatore Siculo** 🧢  (SQL executor and visualizator). Just launched its **v1.0**. fun, safe, and smart!
* 🔶 **Trixie** 📗 (Beatrix “Trixie” Tabularasa) WIP. A Google Sheet agent.
* 🔶 **Vicky** 🟡 (Vicky Pedyah) WIP. A Wikipedia curler on steroids.


![A group of robotic super friends who are LLM agents. They're dressed as super heroes. Very colorful, and they integrate with each other. they rensemble DC Leage of Super Friends](super-friends.png)

A group of robotic super friends who are LLM agents. They're dressed as super heroes. Very colorful, and they integrate with each other.
they rensemble DC Leage of Super Friends

![A group of cute robotic super friends who are LLM agents. They're dressed as super heroes. Very colorful, and they integrate with each other.
they rensemble DC Leage of Super Friends.
Remove DC logos. Make sure the diversity is there, half are females and they're mostly italian.](super-amici-imagen3.png)

![A group of 8 cute robotic super friends who are LLM agents. They're dressed as super heroes. Very colorful, and they integrate with each other.
they rensemble DC Leage of Super Friends.
Remove DC logos. Make sure the diversity is there, half are females and they're mostly italian.
Be inspired by the four Google  colors (red blue yellow and green).
They should be friendly and useful, not scary.](super-friends-googley.png)

![alt text](<super friends v4.png>)

![A group of 8 cute robotic super friends who are LLM agents. They're dressed as super heroes. Very colorful, and they integrate with each other.
they rensemble DC Leage of Super Friends.
NO DC logos. Make sure the diversity is there, half are females and they're mostly italian.
Be inspired by the four Google  colors (red blue yellow and green).
They should be friendly and useful, not scary.
IN front of them, Alfred the butler (also a cute robot) dressed elegantly who opens the door to the Bat cave, in front of a big medieval door.](<super friends with alfred.png>)

More: go/ricc-personal-agents

Coming soon:

* 🔴 **Crudo** (Cloud Run agent). Coming soon.
* 🔴 **Gitti** (`git` agent). Tells you things like "were you drunk when you pushed the latest commit?`. Coming soon.

## Notes on installation

### Trixie

For trixie, you need to:

1. create a service account (say `sa@mail.com`) and store it's key locally, eg under: `private/my-sa-key.json`
2. Then you need to export this as a ENV: `GOOGLE_APPLICATION_CREDENTIALS=private/my-sa-key.json`
3. Finally, you need to share your spreadsheet in READ-ONLY mode to the SA email.

## Serpeverde

* Get a SERP API key in https://serpapi.com

## Deploy to Cloud Run

Let's deploy the agent to Cloud Run with the dev UI enabled.

1. First make sure the necessary APIs are enabled: `just deploy-setup-once`.
2. Then, deploy using the adk tool: `just deploy-alfred`

This builds a container for the agent and deploys to Cloud Run.
You can visit the default URL of the Cloud Run service to interact with the agent.
