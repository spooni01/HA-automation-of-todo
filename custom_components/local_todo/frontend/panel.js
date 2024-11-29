class LocalTodoPanel extends HTMLElement {
    set hass(hass) {
        this.innerHTML = `
            <div>
                <h1>Local To-do integration.</h1> 
                <p>TBD</p>
            </div>
        `;
    }
}

customElements.define("local-todo-new-panel", LocalTodoPanel);