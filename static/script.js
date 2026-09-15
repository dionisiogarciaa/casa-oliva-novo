/**
 * CASA OLIVA - CARDÁPIO DIGITAL & RISTORANTE
 * Vanilla JavaScript (ES6+) Puro - Sem Frameworks Externos
 */

// 1. DADOS DO CARDÁPIO (EXATAMENTE 150 ITENS: 5 CATEGORIAS x 30 ITENS)
const MENU_PRODUCTS = [];


const CATEGORY_IMAGE_POOLS = {
  'ENTRADAS': [
    'https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1592417817098-8f3d6910985b?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1541529086526-db283c563270?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80'
  ],
  'PRATO PRINCIPAL': [
    'https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'
  ],
  'SOBREMESAS': [
    'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=800&q=80'
  ],
  'BEBIDAS': [
    'https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1608270104840-06eb8b16cb2c?auto=format&fit=crop&w=800&q=80'
  ],
  'CARTA DE VINHOS': [
    'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1569919659476-f0852f6834b7?auto=format&fit=crop&w=800&q=80'
  ]
};

function getProductImage(product) {
  const pool = CATEGORY_IMAGE_POOLS[product.categoria] || CATEGORY_IMAGE_POOLS['ENTRADAS'];
  return pool[(Number(product.id) - 1) % pool.length];
}

// 2. ESTADO GLOBAL DA APLICAÇÃO
const AppState = {
  products: [],
  filteredProducts: [],
  selectedCategory: 'TODAS',
  searchQuery: '',
  maxPrice: 1900,
  sortBy: 'padrao',
  cart: [],
  waiterTipEnabled: true,
  theme: 'dark',
  lastOrder: null
};

const STORAGE_KEYS = {
  CART: 'casa_oliva_cart_v1',
  WAITER_TIP: 'casa_oliva_tip_v1',
  THEME: 'casa_oliva_theme_v1'
};

async function loadProductsFromApi() {
  const response = await fetch('/api/products');
  if (!response.ok) throw new Error('Não foi possível carregar o cardápio do SQLite.');
  const payload = await response.json();
  AppState.products = payload.products || [];
  AppState.filteredProducts = [...AppState.products];
  const allCounter = document.getElementById('countAll');
  if (allCounter) allCounter.textContent = AppState.products.length;
  document.querySelectorAll('.category-chip .chip-counter').forEach(counter => {
    const category = counter.closest('.category-chip')?.dataset.category;
    if (category && category !== 'TODAS') {
      counter.textContent = AppState.products.filter(item => item.categoria === category).length;
    }
  });
}
// 3. UTILITÁRIOS
function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2
  }).format(value || 0);
}

function normalizeString(str) {
  return (str || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();
}

function showToast(message, duration = 3000) {
  const container = document.getElementById('toastNotification');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>✦</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, duration);
}

// 4. PERSISTÊNCIA EM LOCALSTORAGE
function loadStateFromStorage() {
  try {
    const savedCart = localStorage.getItem(STORAGE_KEYS.CART);
    if (savedCart) {
      AppState.cart = JSON.parse(savedCart);
    }

    const savedTip = localStorage.getItem(STORAGE_KEYS.WAITER_TIP);
    if (savedTip !== null) {
      AppState.waiterTipEnabled = savedTip === 'true';
    }

    const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME);
    if (savedTheme) {
      AppState.theme = savedTheme;
    }
  } catch (error) {
    console.error('Erro ao ler localStorage:', error);
  }
}

function saveCartToStorage() {
  try {
    localStorage.setItem(STORAGE_KEYS.CART, JSON.stringify(AppState.cart));
  } catch (error) {
    console.error('Erro ao salvar carrinho:', error);
  }
}

function saveTipToStorage() {
  try {
    localStorage.setItem(STORAGE_KEYS.WAITER_TIP, String(AppState.waiterTipEnabled));
  } catch (error) {
    console.error('Erro ao salvar taxa:', error);
  }
}

function saveThemeToStorage() {
  try {
    localStorage.setItem(STORAGE_KEYS.THEME, AppState.theme);
  } catch (error) {
    console.error('Erro ao salvar tema:', error);
  }
}

// 5. MODO CLARO / ESCURO
function applyTheme(theme) {
  AppState.theme = theme;
  document.body.setAttribute('data-theme', theme);
  saveThemeToStorage();
}

function toggleTheme() {
  const nextTheme = AppState.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  showToast(`Modo ${nextTheme === 'dark' ? 'Escuro' : 'Claro'} ativado`);
}

// 6. FILTRO E ORDENAÇÃO
function applyFiltersAndSorting() {
  const query = normalizeString(AppState.searchQuery);
  const selectedCat = AppState.selectedCategory;
  const maxPrice = Number(AppState.maxPrice);

  let result = AppState.products.filter(item => {
    const matchesCategory = selectedCat === 'TODAS' || item.categoria === selectedCat;
    const matchesPrice = item.preco <= maxPrice;

    let matchesSearch = true;
    if (query) {
      const nameNorm = normalizeString(item.nome);
      const descNorm = normalizeString(item.descricao);
      matchesSearch = nameNorm.includes(query) || descNorm.includes(query);
    }

    return matchesCategory && matchesPrice && matchesSearch;
  });

  switch (AppState.sortBy) {
    case 'preco-asc':
      result.sort((a, b) => a.preco - b.preco);
      break;
    case 'preco-desc':
      result.sort((a, b) => b.preco - a.preco);
      break;
    case 'nome-asc':
      result.sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
      break;
    case 'padrao':
    default:
      result.sort((a, b) => a.id - b.id);
      break;
  }

  AppState.filteredProducts = result;
  renderProductsGrid();
  updateResultsSummary();
}

function updateResultsSummary() {
  const countEl = document.getElementById('resultsCount');
  const indicatorEl = document.getElementById('activeFilterIndicator');
  const clearBtn = document.getElementById('clearSearchBtn');

  const total = AppState.filteredProducts.length;
  if (countEl) {
    countEl.textContent = `Exibindo ${total} ${total === 1 ? 'criação culinária' : 'criações culinárias'}`;
  }

  if (indicatorEl) {
    let text = `Categoria: ${AppState.selectedCategory === 'TODAS' ? 'Todas' : AppState.selectedCategory}`;
    if (AppState.searchQuery) {
      text += ` • Busca: "${AppState.searchQuery}"`;
    }
    indicatorEl.textContent = text;
  }

  if (clearBtn) {
    clearBtn.style.display = AppState.searchQuery ? 'flex' : 'none';
  }
}

// 7. RENDERIZAÇÃO DO GRID DE PRODUTOS
function renderProductsGrid() {
  const grid = document.getElementById('productsGrid');
  const emptyState = document.getElementById('emptyState');
  if (!grid || !emptyState) return;

  const items = AppState.filteredProducts;

  if (items.length === 0) {
    grid.innerHTML = '';
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';

  const cardsHtml = items.map(product => {
    return `
      <article class="product-card" data-id="${product.id}">
        <div class="card-media-wrapper">
          <img 
            src="${getProductImage(product)}" 
            alt="${product.nome}" 
            class="card-img" 
            loading="lazy"
            onerror="this.src='https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'"
          >
          <span class="card-category-tag">${product.categoria}</span>
        </div>
        <div class="card-body">
          <div class="card-title-row">
            <h3 class="card-product-name">${product.nome}</h3>
          </div>
          <p class="card-product-desc">${product.descricao}</p>
          <div class="card-footer">
            <div class="card-price-block">
              <span class="card-price-label">Valor unitário</span>
              <span class="card-product-price">${formatCurrency(product.preco)}</span>
            </div>
            <button 
              type="button" 
              class="btn-add-cart" 
              onclick="addToCart(${product.id})"
              aria-label="Adicionar ${product.nome} ao pedido"
            >
              <span class="btn-icon-plus">+</span>
              <span>Adicionar ao pedido</span>
            </button>
          </div>
        </div>
      </article>
    `;
  }).join('');

  grid.innerHTML = cardsHtml;
}

// 8. CARRINHO ("MEU PEDIDO")
function addToCart(productId) {
  const product = AppState.products.find(p => p.id === productId);
  if (!product) return;

  const existingItem = AppState.cart.find(item => item.id === productId);

  if (existingItem) {
    existingItem.quantidade += 1;
  } else {
    AppState.cart.push({
      id: product.id,
      nome: product.nome,
      preco: product.preco,
      categoria: product.categoria,
      imagem: getProductImage(product),
      quantidade: 1
    });
  }

  saveCartToStorage();
  updateCartUI();
  showToast(`"${product.nome}" adicionado ao pedido!`);
}

function updateCartItemQuantity(productId, delta) {
  const itemIndex = AppState.cart.findIndex(item => item.id === productId);
  if (itemIndex === -1) return;

  const item = AppState.cart[itemIndex];
  const newQty = item.quantidade + delta;

  if (newQty <= 0) {
    removeFromCart(productId);
    return;
  }

  item.quantidade = newQty;
  saveCartToStorage();
  updateCartUI();
}

function removeFromCart(productId) {
  const itemToRemove = AppState.cart.find(i => i.id === productId);
  AppState.cart = AppState.cart.filter(item => item.id !== productId);
  saveCartToStorage();
  updateCartUI();

  if (itemToRemove) {
    showToast(`"${itemToRemove.nome}" removido.`);
  }
}

function clearCart() {
  if (AppState.cart.length === 0) return;

  if (confirm("Deseja realmente esvaziar todos os itens do seu pedido?")) {
    AppState.cart = [];
    saveCartToStorage();
    updateCartUI();
    showToast("Comanda esvaziada.");
  }
}

function calculateCartTotals() {
  const subtotal = AppState.cart.reduce((acc, item) => {
    return acc + (item.preco * item.quantidade);
  }, 0);

  const totalUnits = AppState.cart.reduce((acc, item) => acc + item.quantidade, 0);
  const waiterTip = AppState.waiterTipEnabled ? subtotal * 0.10 : 0.0;
  const grandTotal = subtotal + waiterTip;

  return {
    subtotal,
    waiterTip,
    grandTotal,
    totalUnits
  };
}

function updateCartUI() {
  const { subtotal, waiterTip, grandTotal, totalUnits } = calculateCartTotals();

  const badgeEl = document.getElementById('cartBadge');
  const headerTotalEl = document.getElementById('headerCartTotal');
  const drawerCountEl = document.getElementById('drawerItemsCount');

  if (badgeEl) badgeEl.textContent = totalUnits;
  if (headerTotalEl) headerTotalEl.textContent = formatCurrency(grandTotal);
  if (drawerCountEl) {
    drawerCountEl.textContent = `${totalUnits} ${totalUnits === 1 ? 'item selecionado' : 'itens selecionados'}`;
  }

  const subtotalEl = document.getElementById('cartSubtotal');
  const tipEl = document.getElementById('waiterTipValue');
  const grandTotalEl = document.getElementById('cartGrandTotal');
  const tipCheckbox = document.getElementById('waiterTipCheckbox');

  if (subtotalEl) subtotalEl.textContent = formatCurrency(subtotal);
  if (tipEl) {
    tipEl.textContent = AppState.waiterTipEnabled 
      ? `+ ${formatCurrency(waiterTip)}` 
      : 'R$ 0,00';
  }
  if (grandTotalEl) grandTotalEl.textContent = formatCurrency(grandTotal);
  if (tipCheckbox) tipCheckbox.checked = AppState.waiterTipEnabled;

  const listContainer = document.getElementById('cartItemsList');
  const emptyMsg = document.getElementById('cartEmptyMessage');

  if (!listContainer || !emptyMsg) return;

  if (AppState.cart.length === 0) {
    listContainer.innerHTML = '';
    emptyMsg.style.display = 'block';
  } else {
    emptyMsg.style.display = 'none';

    listContainer.innerHTML = AppState.cart.map(item => {
      const itemSubtotal = item.preco * item.quantidade;

      return `
        <div class="cart-item-card" data-id="${item.id}">
          <img 
            src="${getProductImage(item)}" 
            alt="${item.nome}" 
            class="cart-item-thumb"
            onerror="this.src='https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'"
          >
          <div class="cart-item-details">
            <h4 class="cart-item-name">${item.nome}</h4>
            <div class="cart-item-price-line">
              Unitário: <span class="cart-item-price-unit">${formatCurrency(item.preco)}</span>
            </div>
            <div class="cart-item-actions-row">
              <div class="qty-stepper">
                <button 
                  type="button" 
                  class="qty-btn" 
                  onclick="updateCartItemQuantity(${item.id}, -1)"
                  aria-label="Diminuir quantidade"
                >-</button>
                <span class="qty-value">${item.quantidade}</span>
                <button 
                  type="button" 
                  class="qty-btn" 
                  onclick="updateCartItemQuantity(${item.id}, 1)"
                  aria-label="Aumentar quantidade"
                >+</button>
              </div>
              <span class="cart-item-subtotal">${formatCurrency(itemSubtotal)}</span>
            </div>
          </div>
          <button 
            type="button" 
            class="btn-remove-item" 
            onclick="removeFromCart(${item.id})"
            title="Remover item da comanda"
            aria-label="Remover ${item.nome}"
          >&times;</button>
        </div>
      `;
    }).join('');
  }
}

// 9. DRAWER DO CARRINHO
function openCartDrawer() {
  const drawer = document.getElementById('cartDrawer');
  const overlay = document.getElementById('cartOverlay');
  if (drawer && overlay) {
    drawer.classList.add('open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeCartDrawer() {
  const drawer = document.getElementById('cartDrawer');
  const overlay = document.getElementById('cartOverlay');
  if (drawer && overlay) {
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }
}

// 9.1. RECIBO TÉRMICO / MAQUINETA
function populateReceipt(order) {
  if (!order) return;
  const receiptDate = new Date(order.createdAt);
  const receiptTimestamp = `${receiptDate.toLocaleDateString('pt-BR')} · ${receiptDate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
  document.getElementById('receiptOrderNumber').textContent = `COMANDA #${order.number}`;
  document.getElementById('receiptTimestamp').textContent = receiptTimestamp;
  document.getElementById('receiptClient').textContent = `CLIENTE: ${order.clientName}`;
  document.getElementById('receiptTable').textContent = `MESA: ${order.tableNumber}`;
  document.getElementById('receiptSubtotal').textContent = formatCurrency(order.subtotal);
  document.getElementById('receiptGrandTotal').textContent = formatCurrency(order.grandTotal);
  document.getElementById('receiptPayment').textContent = `PAGAMENTO: ${order.paymentMethod}`;
  const receiptTipLine = document.getElementById('receiptTipLine');
  receiptTipLine.style.display = order.waiterTipEnabled ? 'flex' : 'none';
  if (order.waiterTipEnabled) document.getElementById('receiptTip').textContent = formatCurrency(order.waiterTip);
  document.getElementById('receiptItems').innerHTML = order.items.map(item => `
    <div class="receipt-item-row"><span class="receipt-item-name"><span class="receipt-item-qty">${item.quantidade}x</span> ${item.nome}</span><strong>${formatCurrency(item.preco * item.quantidade)}</strong></div>
  `).join('');
  const receiptNotes = document.getElementById('receiptNotes');
  receiptNotes.style.display = order.notes ? 'block' : 'none';
  receiptNotes.textContent = order.notes ? `OBS: ${order.notes}` : '';
}

function openReceipt() {
  if (!AppState.lastOrder) {
    showToast('Finalize um pedido para emitir o recibo.');
    return;
  }
  populateReceipt(AppState.lastOrder);
  const backdrop = document.getElementById('receiptBackdrop');
  backdrop?.classList.add('open');
  backdrop?.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeReceipt() {
  const backdrop = document.getElementById('receiptBackdrop');
  backdrop?.classList.remove('open');
  backdrop?.setAttribute('aria-hidden', 'true');
}

function escapeXml(value) {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}

function downloadReceipt() {
  const order = AppState.lastOrder;
  if (!order) return;
  const lineHeight = 25;
  const lines = [
    ['CASA OLIVA', 24, 26, 'bold', 20],
    ['RISTORANTE & VINOTECA', 24, 51, 'bold', 11],
    ['Rua das Oliveiras, 118 · Jardins · São Paulo/SP', 24, 75, 'normal', 9],
    ['CNPJ 12.345.678/0001-90', 24, 91, 'normal', 9],
    [`COMANDA #${order.number} · MESA ${order.tableNumber}`, 24, 120, 'bold', 10],
    [`CLIENTE: ${order.clientName}`, 24, 138, 'normal', 10],
    ['--------------------------------', 24, 162, 'normal', 10]
  ];
  order.items.forEach((item, index) => {
    const y = 190 + index * lineHeight;
    lines.push([`${item.quantidade}x ${item.nome}`.slice(0, 40), 24, y, 'normal', 10]);
    lines.push([formatCurrency(item.preco * item.quantidade), 300, y, 'bold', 10]);
  });
  const totalsY = 205 + order.items.length * lineHeight;
  lines.push(['--------------------------------', 24, totalsY, 'normal', 10]);
  lines.push([`SUBTOTAL   ${formatCurrency(order.subtotal)}`, 24, totalsY + 25, 'bold', 10]);
  lines.push([order.waiterTipEnabled ? `GARÇOM 10% ${formatCurrency(order.waiterTip)}` : 'GARÇOM 10% NÃO INCLUÍDO', 24, totalsY + 48, 'normal', 10]);
  lines.push([`TOTAL      ${formatCurrency(order.grandTotal)}`, 24, totalsY + 76, 'bold', 13]);
  lines.push([`PAGAMENTO: ${order.paymentMethod}`, 24, totalsY + 102, 'normal', 10]);
  lines.push(['OBRIGADO PELA VISITA · VOLTE SEMPRE', 24, totalsY + 139, 'bold', 10]);
  const height = totalsY + 170;
  const textNodes = lines.map(([text, x, y, weight, size]) => `<text x="${x}" y="${y}" font-family="Courier New, monospace" font-size="${size}px" font-weight="${weight}" fill="#24251f">${escapeXml(text)}</text>`).join('');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="${height}" viewBox="0 0 360 ${height}"><rect width="360" height="${height}" fill="#f2efdf"/>${textNodes}</svg>`;
  const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml;charset=utf-8' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `casa-oliva-recibo-${order.number}.svg`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
  showToast('Recibo salvo como imagem SVG limpa.');
}

// 10. FINALIZAÇÃO DO PEDIDO (CHECKOUT)
async function validateAndCheckout() {
  if (AppState.cart.length === 0) {
    alert("Seu pedido está vazio! Escolha pelo menos um prato antes de finalizar.");
    return;
  }
  const nameInput = document.getElementById('clientNameInput');
  const tableInput = document.getElementById('tableNumberInput');
  const paymentSelect = document.getElementById('paymentMethodSelect');
  const notesTextarea = document.getElementById('orderNotesInput');
  const nameField = nameInput?.closest('.form-field');
  const tableField = tableInput?.closest('.form-field');
  const paymentField = paymentSelect?.closest('.form-field');
  [nameField, tableField, paymentField].forEach(field => field?.classList.remove('has-error'));
  let hasError = false;
  const clientName = nameInput?.value.trim();
  if (!clientName) { nameField?.classList.add('has-error'); hasError = true; }
  const tableNumber = tableInput?.value.trim();
  if (!tableNumber || Number(tableNumber) <= 0) { tableField?.classList.add('has-error'); hasError = true; }
  const paymentMethod = paymentSelect?.value;
  if (!paymentMethod) { paymentField?.classList.add('has-error'); hasError = true; }
  if (hasError) { showToast("Por favor, preencha os campos obrigatórios assinalados."); return; }

  const { subtotal, waiterTip, grandTotal } = calculateCartTotals();
  const orderNotes = notesTextarea?.value.trim() || '';
  const checkoutBtn = document.getElementById('checkoutBtn');
  if (checkoutBtn) { checkoutBtn.disabled = true; checkoutBtn.classList.add('is-loading'); }
  try {
    const response = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cliente: clientName,
        mesa: tableNumber,
        pagamento: paymentMethod,
        observacoes: orderNotes,
        taxa_servico: AppState.waiterTipEnabled,
        itens: AppState.cart.map(item => ({ produto_id: item.id, quantidade: item.quantidade }))
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Não foi possível registrar o pedido.');
    const order = result.order;
    const now = new Date(order.criado_em || Date.now());
    AppState.lastOrder = {
      number: order.numero,
      createdAt: now.toISOString(),
      clientName: order.cliente,
      tableNumber: order.mesa,
      paymentMethod: order.pagamento,
      notes: order.observacoes || '',
      subtotal: Number(order.subtotal),
      waiterTip: Number(order.taxa_servico),
      grandTotal: Number(order.total),
      waiterTipEnabled: Boolean(order.taxa_servico),
      items: order.itens.map(item => ({ ...item, nome: item.nome, preco: Number(item.preco), quantidade: Number(item.quantidade) }))
    };
    populateReceipt(AppState.lastOrder);
    document.getElementById('modalOrderCode').textContent = `#${order.numero}`;
    document.getElementById('modalTimestamp').textContent = `Enviado em ${now.toLocaleDateString('pt-BR')} às ${now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
    document.getElementById('modalClientName').textContent = clientName;
    document.getElementById('modalTableNumber').textContent = `Mesa ${tableNumber}`;
    document.getElementById('modalPaymentMethod').textContent = paymentMethod;
    const summaryContainer = document.getElementById('modalItemsSummary');
    if (summaryContainer) summaryContainer.innerHTML = AppState.lastOrder.items.map(item => `<div class="modal-item-row"><div class="modal-item-left"><span class="modal-item-qty">${item.quantidade}x</span><span class="modal-item-name">${item.nome}</span></div><span class="modal-item-price">${formatCurrency(item.preco * item.quantidade)}</span></div>`).join('');
    const notesWrapper = document.getElementById('modalNotesWrapper');
    const notesEl = document.getElementById('modalNotesText');
    if (orderNotes && notesWrapper && notesEl) { notesEl.textContent = orderNotes; notesWrapper.style.display = 'block'; } else if (notesWrapper) notesWrapper.style.display = 'none';
    document.getElementById('modalSubtotal').textContent = formatCurrency(Number(order.subtotal));
    const tipRow = document.getElementById('modalTipRow');
    const tipModalEl = document.getElementById('modalTip');
    if (AppState.waiterTipEnabled) { tipRow.style.display = 'flex'; tipModalEl.textContent = formatCurrency(Number(order.taxa_servico)); } else tipRow.style.display = 'none';
    document.getElementById('modalGrandTotal').textContent = formatCurrency(Number(order.total));
    closeCartDrawer();
    openConfirmationModal();
    AppState.cart = [];
    saveCartToStorage();
    updateCartUI();
    if (nameInput) nameInput.value = '';
    if (tableInput) tableInput.value = '';
    if (paymentSelect) paymentSelect.value = '';
    if (notesTextarea) notesTextarea.value = '';
  } catch (error) {
    showToast(error.message || 'Erro ao registrar pedido no SQLite.');
  } finally {
    if (checkoutBtn) { checkoutBtn.disabled = false; checkoutBtn.classList.remove('is-loading'); }
  }
}
function openConfirmationModal() {
  const modal = document.getElementById('confirmationModal');
  if (modal) {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeConfirmationModal() {
  const modal = document.getElementById('confirmationModal');
  if (modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }
}

// 11. BINDINGS DE EVENTOS
function setupEventListeners() {
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.addEventListener('click', toggleTheme);
  }

  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      AppState.searchQuery = e.target.value;
      applyFiltersAndSorting();
    });
  }

  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      AppState.searchQuery = '';
      applyFiltersAndSorting();
      searchInput?.focus();
    });
  }

  const categoryChips = document.querySelectorAll('.category-chip');
  categoryChips.forEach(chip => {
    chip.addEventListener('click', () => {
      categoryChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      AppState.selectedCategory = chip.getAttribute('data-category') || 'TODAS';
      applyFiltersAndSorting();
    });
  });

  const footerCatLinks = document.querySelectorAll('[data-footer-cat]');
  footerCatLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetCat = link.getAttribute('data-footer-cat');
      const matchingChip = document.querySelector(`.category-chip[data-category="${targetCat}"]`);
      if (matchingChip) {
        matchingChip.click();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  });

  const priceSlider = document.getElementById('priceRangeFilter');
  const priceDisplay = document.getElementById('priceRangeValue');

  if (priceSlider) {
    priceSlider.addEventListener('input', (e) => {
      const val = Number(e.target.value);
      AppState.maxPrice = val;
      if (priceDisplay) {
        priceDisplay.textContent = formatCurrency(val);
      }
      applyFiltersAndSorting();
    });
  }

  const sortSelect = document.getElementById('sortOrderSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      AppState.sortBy = e.target.value;
      applyFiltersAndSorting();
    });
  }

  const resetBtn = document.getElementById('resetFiltersBtn');
  const emptyResetBtn = document.getElementById('emptyResetBtn');

  const resetAll = () => {
    AppState.searchQuery = '';
    AppState.selectedCategory = 'TODAS';
    AppState.maxPrice = 1900;
    AppState.sortBy = 'padrao';

    if (searchInput) searchInput.value = '';
    if (priceSlider) priceSlider.value = '1900';
    if (priceDisplay) priceDisplay.textContent = 'R$ 1.900';
    if (sortSelect) sortSelect.value = 'padrao';

    categoryChips.forEach(c => {
      if (c.getAttribute('data-category') === 'TODAS') {
        c.classList.add('active');
      } else {
        c.classList.remove('active');
      }
    });

    applyFiltersAndSorting();
    showToast("Filtros restaurados.");
  };

  resetBtn?.addEventListener('click', resetAll);
  emptyResetBtn?.addEventListener('click', resetAll);

  document.getElementById('openCartBtn')?.addEventListener('click', openCartDrawer);
  document.getElementById('closeCartBtn')?.addEventListener('click', closeCartDrawer);
  document.getElementById('cartOverlay')?.addEventListener('click', closeCartDrawer);

  const tipCheckbox = document.getElementById('waiterTipCheckbox');
  if (tipCheckbox) {
    tipCheckbox.addEventListener('change', (e) => {
      AppState.waiterTipEnabled = e.target.checked;
      saveTipToStorage();
      updateCartUI();
    });
  }

  document.getElementById('clearCartBtn')?.addEventListener('click', clearCart);
  document.getElementById('checkoutBtn')?.addEventListener('click', validateAndCheckout);

  document.getElementById('closeModalBtn')?.addEventListener('click', closeConfirmationModal);
  document.getElementById('confirmationModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'confirmationModal') {
      closeConfirmationModal();
    }
  });

  document.getElementById('printOrderBtn')?.addEventListener('click', openReceipt);
  document.getElementById('downloadReceiptBtn')?.addEventListener('click', downloadReceipt);
  document.getElementById('receiptPrintBtn')?.addEventListener('click', () => window.print());
  document.getElementById('closeReceiptBtn')?.addEventListener('click', closeReceipt);
  document.getElementById('closeReceiptSecondaryBtn')?.addEventListener('click', closeReceipt);
  document.getElementById('receiptBackdrop')?.addEventListener('click', (e) => {
    if (e.target.id === 'receiptBackdrop') closeReceipt();
  });
  document.getElementById('receiptPaper')?.addEventListener('dblclick', () => window.print());

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeCartDrawer();
      closeConfirmationModal();
      closeReceipt();
    }
  });
}

// 12. INICIALIZAÇÃO
document.addEventListener('DOMContentLoaded', async () => {
  try { await loadProductsFromApi(); } catch (error) { showToast(error.message || 'Erro ao carregar o cardápio.'); }
  loadStateFromStorage();
  applyTheme(AppState.theme);
  setupEventListeners();
  applyFiltersAndSorting();
  updateCartUI();
  console.log("Casa Oliva Ristorante: Cardápio carregado com sucesso (150 pratos).");
});
