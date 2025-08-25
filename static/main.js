// static/main.js

document.addEventListener('DOMContentLoaded', () => {
    const apiBaseUrl = 'http://localhost:8000';
    // Retrieve the token from sessionStorage
    const authToken = sessionStorage.getItem('authToken');
    
    // If no token, redirect to login page
    if (!authToken) {
        window.location.href = '/';
        return;
    }

    let brandChart = null;
    let conditionChart = null;

    // --- Pagination State ---
    let currentPage = 1;
    const itemsPerPage = 15;
    let totalItems = 0;

    // --- DOM Elements ---
    const phoneInventoryBody = document.getElementById('phone-inventory-body');
    const showAddPhoneModalBtn = document.getElementById('show-add-phone-modal-btn');
    const phoneModal = document.getElementById('phone-modal');
    const modalTitle = document.getElementById('modal-title');
    const phoneForm = document.getElementById('phone-form');
    const saveBtn = document.getElementById('save-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const addSpecBtn = document.getElementById('add-spec-btn');
    const specificationsContainer = document.getElementById('specifications-container');
    const searchBrand = document.getElementById('search-brand');
    const filterCondition = document.getElementById('filter-condition');
    const filterPlatform = document.getElementById('filter-platform');
    const resetFiltersBtn = document.getElementById('reset-filters-btn');
    const updatePricesBtn = document.getElementById('update-prices-btn');
    const csvUpload = document.getElementById('csv-upload');
    const logContainer = document.getElementById('log-container');
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    const modalTabs = document.getElementById('modal-tabs');
    const tagInput = document.getElementById('tag-input');
    const tagsContainer = document.getElementById('tags-container');
    const listingsContainer = document.getElementById('listings-container');
    const notificationContainer = document.getElementById('notification-container');
    const confirmationModal = document.getElementById('confirmation-modal');
    const confirmationMessage = document.getElementById('confirmation-message');
    const confirmationConfirmBtn = document.getElementById('confirmation-confirm-btn');
    const confirmationCancelBtn = document.getElementById('confirmation-cancel-btn');
    const bulkListPlatform = document.getElementById('bulk-list-platform');
    const bulkListBtn = document.getElementById('bulk-list-btn');
    const paginationInfo = document.getElementById('pagination-info');
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');

    // --- Professional Enhancements ---
    const debounce = (func, delay) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    };

    const showLoadingState = (isLoading) => {
        if (isLoading) {
            phoneInventoryBody.innerHTML = `<tr><td colspan="5" class="text-center py-10"><div class="loader mx-auto"></div></td></tr>`;
        }
    };

    const apiFetch = async (url, options = {}) => {
        const headers = {
            'Authorization': `Bearer ${authToken}`,
            ...options.headers,
        };
        const response = await fetch(url, { ...options, headers });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'An unknown server error occurred' }));
            throw new Error(errorData.detail);
        }
        if (response.status === 204) {
            return null;
        }
        return response.json();
    };

    // --- Notification System ---
    const showNotification = (message, type = 'success') => {
        const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
        const notification = document.createElement('div');
        notification.className = `text-white p-3 rounded-lg shadow-lg animate-pulse ${bgColor}`;
        notification.textContent = message;
        notificationContainer.appendChild(notification);
        setTimeout(() => {
            notification.remove();
        }, 4000);
    };

    // --- Confirmation Modal System ---
    const showConfirmationModal = (message, onConfirm) => {
        confirmationMessage.textContent = message;
        confirmationModal.classList.add('active');
        const confirmHandler = () => {
            onConfirm();
            confirmationModal.classList.remove('active');
            confirmationConfirmBtn.removeEventListener('click', confirmHandler);
        };
        const cancelHandler = () => {
            confirmationModal.classList.remove('active');
            confirmationCancelBtn.removeEventListener('click', cancelHandler);
            confirmationConfirmBtn.removeEventListener('click', confirmHandler);
        };
        confirmationConfirmBtn.addEventListener('click', confirmHandler, { once: true });
        confirmationCancelBtn.addEventListener('click', cancelHandler, { once: true });
    };

    // --- Data Fetching and Rendering ---
    const fetchAllData = () => {
        fetchDashboardAnalytics();
        fetchPhones();
        fetchLogs();
    };

    const fetchDashboardAnalytics = async () => {
        const params = new URLSearchParams({
            brand: searchBrand.value,
            condition: filterCondition.value,
            platform: filterPlatform.value,
        });
        try {
            const data = await apiFetch(`${apiBaseUrl}/dashboard/analytics?${params.toString()}`);
            document.getElementById('total-phones').textContent = data.total_phones || 0;
            document.getElementById('total-stock-units').textContent = data.total_stock_units || 0;
            document.getElementById('total-inventory-value').textContent = `$${(data.total_inventory_value || 0).toLocaleString()}`;
            renderCharts(data.stock_by_brand, data.stock_by_condition);
        } catch (error) {
            showNotification(`Could not load analytics: ${error.message}`, 'error');
        }
    };

    const fetchPhones = async () => {
        showLoadingState(true);
        const skip = (currentPage - 1) * itemsPerPage;
        const params = new URLSearchParams({
            skip,
            limit: itemsPerPage,
            brand: searchBrand.value,
            condition: filterCondition.value,
            platform: filterPlatform.value,
        });
        
        try {
            const data = await apiFetch(`${apiBaseUrl}/phones?${params.toString()}`);
            totalItems = data.total_items;
            renderPhones(data.items);
            renderPagination();
        } catch (error) {
            showNotification(`Could not load phones: ${error.message}`, 'error');
            phoneInventoryBody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-red-500">Error loading data.</td></tr>`;
        }
    };

    const fetchLogs = async () => {
        try {
            const logs = await apiFetch(`${apiBaseUrl}/logs`);
            renderLogs(logs);
        } catch (error) {
            logContainer.innerHTML = '<p class="text-red-500">Could not load action logs.</p>';
        }
    };

    const renderPhones = (phones) => {
        if (phones.length === 0) {
            phoneInventoryBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-10">
                        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        <h3 class="mt-2 text-sm font-medium text-slate-900">No phones found</h3>
                        <p class="mt-1 text-sm text-slate-500">Add a new phone or adjust your filters.</p>
                    </td>
                </tr>`;
            return;
        }
        phoneInventoryBody.innerHTML = phones.map(phone => `
            <tr class="hover:bg-slate-50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="font-medium text-slate-900">${phone.model_name}</div>
                    <div class="text-sm text-slate-500">${phone.brand} | ${phone.condition}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-slate-700">${phone.stock_quantity}</td>
                <td class="px-6 py-4 whitespace-nowrap text-slate-700">$${phone.base_price.toFixed(2)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-slate-700">${phone.listed_on.join(', ') || 'None'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex items-center space-x-4">
                        <button class="text-slate-500 hover:text-indigo-600" title="Edit details, manage listings, and override prices" onclick="window.openEditModal(${phone.id})">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" /><path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" /></svg>
                        </button>
                        <button class="text-slate-500 hover:text-red-600" title="Delete" onclick="window.deletePhone(${phone.id})">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    };
    
    const renderLogs = (logs) => {
        logContainer.innerHTML = logs.map(log => `
            <div class="text-sm py-2 border-b border-slate-200">
                <span class="font-semibold text-slate-600">${new Date(log.timestamp).toLocaleString()}</span>: 
                <span class="text-indigo-600 font-medium">${log.action}</span> - 
                <span class="text-slate-700">${log.details}</span>
            </div>
        `).join('') || '<p class="text-slate-500">No actions logged yet.</p>';
    };

    const renderCharts = (brandData, conditionData) => {
        const brandCtx = document.getElementById('brand-chart').getContext('2d');
        if (brandChart) brandChart.destroy();
        brandChart = new Chart(brandCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(brandData),
                datasets: [{ data: Object.values(brandData), backgroundColor: ['#4f46e5', '#ef4444', '#22c55e', '#f97316', '#8b5cf6', '#3b82f6'] }]
            },
            options: { plugins: { title: { display: true, text: 'Stock by Brand', font: { size: 16 } } } }
        });

        const conditionCtx = document.getElementById('condition-chart').getContext('2d');
        if (conditionChart) conditionChart.destroy();
        conditionChart = new Chart(conditionCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(conditionData),
                datasets: [{ label: 'Count', data: Object.values(conditionData), backgroundColor: '#6366f1' }]
            },
            options: { plugins: { title: { display: true, text: 'Inventory by Condition', font: { size: 16 } } } }
        });
    };

    const renderPagination = () => {
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        const startItem = (currentPage - 1) * itemsPerPage + 1;
        const endItem = Math.min(startItem + itemsPerPage - 1, totalItems);

        paginationInfo.textContent = totalItems > 0 ? `Showing ${startItem}-${endItem} of ${totalItems}` : 'No items found';
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = currentPage === totalPages || totalItems === 0;
    };

    // --- Modal and Form Handling ---
    const openModal = (phone = null) => {
        phoneForm.reset();
        specificationsContainer.innerHTML = '';
        tagsContainer.innerHTML = '';
        listingsContainer.innerHTML = '';
        document.querySelectorAll('#phone-modal .tab-content').forEach(tc => tc.classList.remove('active'));
        document.getElementById('tab-details').classList.add('active');
        document.querySelectorAll('#phone-modal .tab-btn').forEach(tb => tb.classList.remove('active'));
        document.querySelector('#phone-modal .tab-btn[data-tab="details"]').classList.add('active');

        if (phone) {
            modalTitle.textContent = `Manage: ${phone.model_name}`;
            document.getElementById('phone-id').value = phone.id;
            document.getElementById('model_name').value = phone.model_name;
            document.getElementById('brand').value = phone.brand;
            document.getElementById('condition').value = phone.condition;
            document.getElementById('stock_quantity').value = phone.stock_quantity;
            document.getElementById('base_price').value = phone.base_price;
            Object.entries(phone.specifications).forEach(([key, value]) => addSpecificationField(key, value));
            
            ['x', 'y', 'z'].forEach(p => {
                document.getElementById(`auto-price-${p}`).textContent = `(Auto: $${phone.platform_prices[p.toUpperCase()].toFixed(2)})`;
                document.getElementById(`override-price-${p}`).value = phone.manual_overrides[p.toUpperCase()] || '';
            });

            renderTags(phone.tags);
            renderListings(phone);

        } else {
            modalTitle.textContent = 'Add New Phone';
            document.getElementById('phone-id').value = '';
            addSpecificationField();
            ['x', 'y', 'z'].forEach(p => {
                document.getElementById(`auto-price-${p}`).textContent = '';
                document.getElementById(`override-price-${p}`).value = '';
            });
            renderTags([]);
            document.querySelector('.tab-btn[data-tab="listings"]').style.display = 'none';
        }
        phoneModal.classList.add('active');
    };

    const closeModal = () => phoneModal.classList.remove('active');

    const addSpecificationField = (key = '', value = '') => {
        const specDiv = document.createElement('div');
        specDiv.className = 'flex space-x-2';
        specDiv.innerHTML = `<input type="text" placeholder="Key" value="${key}" class="p-2 border rounded-md w-1/2 border-slate-300 spec-key"><input type="text" placeholder="Value" value="${value}" class="p-2 border rounded-md w-1/2 border-slate-300 spec-value"><button type="button" class="text-red-500 remove-spec-btn">&times;</button>`;
        specificationsContainer.appendChild(specDiv);
        specDiv.querySelector('.remove-spec-btn').addEventListener('click', () => specDiv.remove());
    };

    const renderTags = (tags) => {
        tagsContainer.innerHTML = '';
        tags.forEach(tag => {
            const tagEl = document.createElement('span');
            tagEl.className = 'bg-indigo-100 text-indigo-800 text-sm font-medium px-2.5 py-0.5 rounded flex items-center';
            tagEl.innerHTML = `${tag} <button type="button" class="ml-2 text-indigo-600 hover:text-indigo-800 remove-tag-btn">&times;</button>`;
            tagsContainer.appendChild(tagEl);
            tagEl.querySelector('.remove-tag-btn').addEventListener('click', () => tagEl.remove());
        });
    };
    
    const renderListings = (phone) => {
        const platforms = ['X', 'Y', 'Z'];
        listingsContainer.innerHTML = '';
        document.querySelector('.tab-btn[data-tab="listings"]').style.display = 'block';

        platforms.forEach(p => {
            const isListed = phone.listed_on.includes(p);
            const listingDiv = document.createElement('div');
            listingDiv.className = 'flex justify-between items-center p-3 border rounded-md border-slate-200';
            listingDiv.innerHTML = `
                <div>
                    <p class="font-bold text-slate-800">Platform ${p}</p>
                    <span class="text-sm ${isListed ? 'text-green-600' : 'text-slate-500'}">${isListed ? 'Listed' : 'Not Listed'}</span>
                </div>
                <button type="button" class="${isListed ? 'bg-slate-200 text-slate-500 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600 text-white'} px-3 py-1 rounded-md transition text-sm font-medium" ${isListed ? 'disabled' : ''} onclick="window.listPhone(${phone.id}, '${p}')">
                    ${isListed ? 'Listed' : 'List Now'}
                </button>
            `;
            listingsContainer.appendChild(listingDiv);
        });
    };

    // --- Event Listeners ---
    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tab = e.currentTarget.dataset.tab;
            sidebarLinks.forEach(l => l.classList.remove('active'));
            e.currentTarget.classList.add('active');
            document.querySelectorAll('.main-tab-content').forEach(tc => tc.classList.remove('active'));
            document.getElementById(`tab-${tab}`).classList.add('active');
        });
    });

    addSpecBtn.addEventListener('click', () => addSpecificationField());
    showAddPhoneModalBtn.addEventListener('click', () => openModal());
    cancelBtn.addEventListener('click', closeModal);
    saveBtn.addEventListener('click', async () => {
        const id = document.getElementById('phone-id').value;
        const specifications = {};
        document.querySelectorAll('#specifications-container .flex').forEach(div => {
            const key = div.querySelector('.spec-key').value;
            const value = div.querySelector('.spec-value').value;
            if (key && value) specifications[key] = value;
        });
        
        const manual_overrides = {
            X: parseFloat(document.getElementById('override-price-x').value) || null,
            Y: parseFloat(document.getElementById('override-price-y').value) || null,
            Z: parseFloat(document.getElementById('override-price-z').value) || null,
        };

        const tags = Array.from(tagsContainer.children).map(el => el.textContent.slice(0, -2).trim());

        const phoneData = {
            model_name: document.getElementById('model_name').value,
            brand: document.getElementById('brand').value,
            condition: document.getElementById('condition').value,
            stock_quantity: parseInt(document.getElementById('stock_quantity').value),
            base_price: parseFloat(document.getElementById('base_price').value),
            specifications,
            manual_overrides,
            tags,
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${apiBaseUrl}/phones/${id}` : `${apiBaseUrl}/phones`;

        try {
            await apiFetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(phoneData)
            });
            showNotification(id ? 'Phone updated successfully!' : 'Phone added successfully!');
            closeModal();
            fetchAllData();
        } catch (error) {
            showNotification(`Error: ${error.message}`, 'error');
        }
    });

    modalTabs.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-btn')) {
            const tab = e.target.dataset.tab;
            document.querySelectorAll('#phone-modal .tab-btn').forEach(tb => tb.classList.remove('active'));
            e.target.classList.add('active');
            document.querySelectorAll('#phone-modal .tab-content').forEach(tc => tc.classList.remove('active'));
            document.getElementById(`tab-${tab}`).classList.add('active');
        }
    });

    tagInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && tagInput.value.trim() !== '') {
            e.preventDefault();
            renderTags([...Array.from(tagsContainer.children).map(el => el.textContent.slice(0, -2).trim()), tagInput.value.trim()]);
            tagInput.value = '';
        }
    });

    const debouncedFetch = debounce(() => {
        currentPage = 1;
        fetchPhones();
        fetchDashboardAnalytics();
    }, 300);

    [searchBrand, filterCondition, filterPlatform].forEach(el => {
        el.addEventListener('input', debouncedFetch);
    });

    resetFiltersBtn.addEventListener('click', () => {
        searchBrand.value = '';
        filterCondition.value = '';
        filterPlatform.value = '';
        currentPage = 1;
        fetchAllData();
    });

    updatePricesBtn.addEventListener('click', () => {
        showConfirmationModal('Are you sure you want to update all platform prices?', async () => {
            try {
                await apiFetch(`${apiBaseUrl}/prices/update`, { method: 'POST' });
                showNotification('All prices updated successfully!');
                fetchAllData();
            } catch (error) {
                showNotification(`Error: ${error.message}`, 'error');
            }
        });
    });

    csvUpload.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        try {
            await apiFetch(`${apiBaseUrl}/phones/upload`, { method: 'POST', body: formData });
            showNotification('Bulk upload successful!');
            currentPage = 1;
            fetchAllData();
        } catch (error) {
            showNotification(`Upload failed: ${error.message}`, 'error');
        }
    });

    bulkListBtn.addEventListener('click', async () => {
        const platform = bulkListPlatform.value;
        if (!platform) {
            showNotification('Please select a platform first.', 'error');
            return;
        }
        
        const params = new URLSearchParams({
            brand: searchBrand.value,
            condition: filterCondition.value,
        });

        showConfirmationModal(`List all filtered phones on Platform ${platform}?`, async () => {
            try {
                const result = await apiFetch(`${apiBaseUrl}/phones/bulk-list/${platform}?${params.toString()}`, { method: 'POST' });
                showNotification(`Bulk list complete. Success: ${result.success}, Failed: ${result.failed}`);
                fetchAllData();
            } catch (error) {
                showNotification(`Bulk list failed: ${error.message}`, 'error');
            }
        });
    });

    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchPhones();
        }
    });

    nextPageBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            fetchPhones();
        }
    });

    // --- Global functions for inline event handlers ---
    window.openEditModal = async (id) => {
        const params = new URLSearchParams({ skip: 0, limit: totalItems });
        try {
            const data = await apiFetch(`${apiBaseUrl}/phones?${params.toString()}`);
            const phone = data.items.find(p => p.id === id);
            if (phone) openModal(phone);
        } catch (error) {
            showNotification(`Could not fetch phone details: ${error.message}`, 'error');
        }
    };

    window.deletePhone = (id) => {
        showConfirmationModal('Are you sure you want to delete this phone?', async () => {
            try {
                await apiFetch(`${apiBaseUrl}/phones/${id}`, { method: 'DELETE' });
                showNotification('Phone deleted successfully.');
                fetchAllData();
            } catch (error) {
                showNotification(`Failed to delete phone: ${error.message}`, 'error');
            }
        });
    };
    
    window.listPhone = async (id, platform) => {
        try {
            const result = await apiFetch(`${apiBaseUrl}/phones/${id}/list/${platform}`, { method: 'POST' });
            showNotification(result.message);
            closeModal();
            fetchAllData();
        } catch (error) {
            showNotification(`Error: ${error.message}`, 'error');
        }
    };

    // Initial load
    fetchAllData();
});
