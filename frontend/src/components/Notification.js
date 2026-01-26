export class Notification {
  constructor(root) {
    this.root = root;
  }
  show(type, message) {
    const el = document.createElement('div');
    el.className = `notice ${type}`;
    el.textContent = message;
    this.root.appendChild(el);
    setTimeout(() => {
      el.remove();
    }, 3000);
  }
}
