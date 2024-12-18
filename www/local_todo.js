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
    };
  }

  constructor() {
    super();
    this.rules = [];
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
    }
  }

  render() {
    return html`
      <wired-card elevation="2">
        <h3>Rules</h3>
        <ul>
          ${this.rules.length > 0
            ? this.rules.map(
                (rule) => html`
                  <li>
                    [${rule[0]}] <strong>${rule[1]}</strong>: ${rule[2]}
                    <br />
                    <em>Trigger:</em> ${rule[3]} (${rule[4]} = ${rule[5]})
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
    `;
  }
}
customElements.define("local-todo-panel", LocalTodoPanel);