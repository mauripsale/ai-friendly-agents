Self: https://github.com/palladius/ai-friendly-agents/

## Agents

My friendly agents:

* 🟡 **Claudia Gugghelheim** ☁️ (Google Cloud agent). WIP Inspired by Cloud: 🔴🔵🟢🟡
* 🟢 **Codie Smulders** 🐍  (code agent). For now, just `built_in_code_execution` from ADK.
* 🟢 **Larry** 🧢  (cURLer / Google). For the moment, just googling is implemented.
* 🟢 **Siculo** 🧢  (SQL executor and visualizator). Just launched its **v1.0**. fun, safe, and smart!
* 🔶 **Trixie** 📗 (Beatrix “Trixie” Tabularasa) WIP. A Google Sheet agent.
* 🔶 **Vicky** 🟡 (Wi “Trixie” Tabularasa) WIP. A Wikipedia curler on steroids.

More: go/ricc-personal-agents

## Notes on installation

### Trixie

For trixie, you need to:

1. create a service account (say `sa@mail.com`) and store it's key locally, eg under: `private/my-sa-key.json`
2. Then you need to export this as a ENV: `GOOGLE_APPLICATION_CREDENTIALS=private/my-sa-key.json`
3. Finally, you need to share your spreadsheet in READ-ONLY mode to the SA email.
