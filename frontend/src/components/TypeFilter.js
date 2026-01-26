export class TypeFilter {
  constructor(root) {
    this.root = root;
    this.select = document.createElement('select');
    this.select.innerHTML = `
      <option value="">All</option>
      <option value="Running">Running</option>
      <option value="Rowing">Rowing</option>
      <option value="Rucking">Rucking</option>
    `;
    this.select.addEventListener('change', () => {
      const ev = new CustomEvent('filterchange', { detail: { type: this.select.value || null } });
      this.root.dispatchEvent(ev);
    });
    this.root.appendChild(this.select);
  }
}
