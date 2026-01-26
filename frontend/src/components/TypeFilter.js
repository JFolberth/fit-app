export class TypeFilter {
  constructor(root) {
    this.root = root;
    this.activeType = null;
    
    const types = [
      { value: '', label: 'All Activities' },
      { value: 'Running', label: '🏃 Running' },
      { value: 'Rowing', label: '🚣 Rowing' },
      { value: 'Rucking', label: '🎒 Rucking' }
    ];
    
    types.forEach((type, index) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'filter-btn' + (index === 0 ? ' active' : '');
      btn.textContent = type.label;
      btn.dataset.value = type.value;
      
      btn.addEventListener('click', () => {
        this.root.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.activeType = type.value || null;
        
        const ev = new CustomEvent('filterchange', { detail: { type: this.activeType } });
        this.root.dispatchEvent(ev);
      });
      
      this.root.appendChild(btn);
    });
  }
}
