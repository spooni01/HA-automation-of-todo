import "https://unpkg.com/wired-card@2.1.0/lib/wired-card.js?module";
import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class LocalTodoPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
      rules: { type: Array },
      entities: { type: Array },
    };
  }

  constructor() {
    super();
    this.rules = [];
    this.entities = [];
    this.newRule = { name: "", description: "", entity_id: "", entity_type_of_change: "", entity_change_value: "" };
  }

  firstUpdated() {
    if (this.hass && this.hass) {
      this.hass.callWS({
          type: "get_local_todo_rules",
        })
        .then((rules) => {
          this.rules = rules.payload;
        })
        .catch((err) => {
          console.error("Error fetching rules via WebSocket:", err);
        });


      const entityIds = Object.keys(this.hass.states);
      this.entities = entityIds.map(id => ({
        id,
        name: this.hass.states[id].attributes.friendly_name || id
      }));

    }
  }

  handleInputChange(e) {
    const { name, value } = e.target;
    this.newRule = { ...this.newRule, [name]: value };
  }

  addNewRule() {
    if (this.hass) {
      this.hass.callWS({
        type: "set_local_todo_rule",
        name: this.newRule.name,
        description: this.newRule.description,
        entity_id: this.newRule.entity_id,
        entity_type_of_change: this.newRule.entity_type_of_change,
        entity_change_value: this.newRule.entity_change_value,
      })
      .then(() => {
        console.log("Rule submitted successfully");
        this.firstUpdated();
      })
      .catch((err) => {
        console.error("Error submitting rule via WebSocket:", err);
      });
    }
  }

  deleteRule(ruleId) {
    if (this.hass) {
      this.hass.callWS({
        type: "delete_local_todo_rule",
        rule_id: ruleId,
      })
      .then(() => {
        console.log(`Rule [${ruleId}] deleted successfully`);
        this.firstUpdated();
      })
      .catch((err) => {
        console.error(`Error deleting rule [${ruleId}] via WebSocket:`, err);
      });
    }
  }

  render() {
    return html`
      <wired-card elevation="2">
        <h3>Add New Rule</h3>
        <label>
          Name:
          <input
            type="text"
            name="name"
            .value=${this.newRule.name}
            @input=${this.handleInputChange}
          />
        </label>
        <label>
          Description:
          <input
            type="text"
            name="description"
            .value=${this.newRule.description}
            @input=${this.handleInputChange}
          />
        </label>
        <label>
          Entity ID:
          <select
            name="entity_id"
            .value=${this.newRule.entity_id}
            @change=${this.handleInputChange}
          >
            <option value="">--Select an entity--</option>
            ${this.entities.map(
              (entity) => html`<option value="${entity.id}">${entity.name} (${entity.id})</option>`
            )}
          </select>
        </label>
        <label>
          Entity Type of Change:
          <input
            type="text"
            name="entity_type_of_change"
            .value=${this.newRule.entity_type_of_change}
            @input=${this.handleInputChange}
          />
        </label>
        <label>
          Entity Change Value:
          <input
            type="text"
            name="entity_change_value"
            .value=${this.newRule.entity_change_value}
            @input=${this.handleInputChange}
          />
        </label>
        <button @click=${this.addNewRule}>Submit</button>

        <h3>Rules</h3>
        <ul>
          ${this.rules.length > 0
            ? this.rules.map(
                (rule) => html`
                  <li>
                    [${rule[0]}] <strong>${rule[1]}</strong>: ${rule[2]}
                    <br />
                    <em>Trigger:</em> ${rule[3]} (${rule[4]} = ${rule[5]})
                    <button @click=${() => this.deleteRule(rule[0])}>Delete rule</button>
                  </li>
                `
              )
            : html`<p>Loading rules...</p>`}
        </ul>
      </wired-card>
    `;
  }

  static get styles() {
    return css`
      :host {
        padding: 16px;
        display: block;
      }
      wired-card {
        padding: 16px;
        display: block;
        font-size: 18px;
        max-width: 600px;
        margin: 0 auto;
      }
      label {
        display: block;
        margin-bottom: 8px;
      }
      input {
        margin-left: 8px;
      }
      button {
        margin-top: 16px;
      }
    `;
  }
}
customElements.define("local-todo-panel", LocalTodoPanel);