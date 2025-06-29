document.addEventListener('DOMContentLoaded', () => {
    const productMessage = document.getElementById('productMessage');
    const productForm = document.getElementById('productForm');
    const productIdInput = document.getElementById('productId');
    const productAsinInput = document.getElementById('productAsin');
    const productNameInput = document.getElementById('productName');
    const productCategoryInput = document.getElementById('productCategory');
    const productAvgSellingPriceInput = document.getElementById('productAvgSellingPrice');
    const productCostOfGoodsSoldInput = document.getElementById('productCostOfGoodsSold');
    const productInitialCvrBaselineInput = document.getElementById('productInitialCvrBaseline');
    const saveProductButton = document.getElementById('saveProductButton');
    const clearFormButton = document.getElementById('clearFormButton');

    const productsTableBody = document.getElementById('productsTableBody');
    const refreshProductsButton = document.getElementById('refreshProductsButton');

    const API_BASE_URL = '/api';

    const displayMessage = (element, message, isError = false) => {
        element.textContent = message;
        element.className = isError ? 'message error' : 'message success';
        element.style.display = 'block';
        setTimeout(() => { element.style.display = 'none'; }, 5000);
    };

    const getToken = () => {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            displayMessage(productMessage, 'Authentication token not found. Please login.', true);
            // window.location.href = '/static/auth.html'; // Consider redirecting
            return null;
        }
        return token;
    };

    const fetchProducts = async () => {
        const token = getToken();
        if (!token) return;

        try {
            const response = await fetch(`${API_BASE_URL}/products/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || `Failed to fetch products: ${response.statusText}`);
            }
            const products = await response.json();
            productsTableBody.innerHTML = ''; // Clear existing rows
            products.forEach(product => {
                const row = productsTableBody.insertRow();
                row.innerHTML = `
                    <td>${product.id}</td>
                    <td>${product.asin}</td>
                    <td>${product.product_name}</td>
                    <td>${product.category || 'N/A'}</td>
                    <td>${parseFloat(product.avg_selling_price).toFixed(2)}</td>
                    <td>${parseFloat(product.cost_of_goods_sold).toFixed(2)}</td>
                    <td>${(parseFloat(product.initial_cvr_baseline) * 100).toFixed(2)}%</td>
                    <td>
                        <button class="edit-btn" data-id="${product.id}">Edit</button>
                        <button class="delete-btn" data-id="${product.id}">Delete</button>
                    </td>
                `;
            });
            attachActionListeners();
        } catch (error) {
            displayMessage(productMessage, error.message, true);
        }
    };

    const attachActionListeners = () => {
        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                await populateFormForEdit(id);
            });
        });
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                if (confirm(`Are you sure you want to delete product ID ${id}?`)) {
                    await deleteProduct(id);
                }
            });
        });
    };

    const populateFormForEdit = async (id) => {
        const token = getToken();
        if (!token) return;
        try {
            const response = await fetch(`${API_BASE_URL}/products/${id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) throw new Error('Failed to fetch product details for editing.');
            const product = await response.json();

            productIdInput.value = product.id;
            productAsinInput.value = product.asin;
            productNameInput.value = product.product_name;
            productCategoryInput.value = product.category || '';
            productAvgSellingPriceInput.value = parseFloat(product.avg_selling_price).toFixed(2);
            productCostOfGoodsSoldInput.value = parseFloat(product.cost_of_goods_sold).toFixed(2);
            productInitialCvrBaselineInput.value = parseFloat(product.initial_cvr_baseline).toFixed(3);
            saveProductButton.textContent = 'Update Product';
            window.scrollTo(0, 0); // Scroll to top to see the form
        } catch (error) {
            displayMessage(productMessage, error.message, true);
        }
    };

    const clearProductForm = () => {
        productForm.reset();
        productIdInput.value = '';
        saveProductButton.textContent = 'Save Product';
    };

    productForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = getToken();
        if (!token) return;

        const productData = {
            asin: productAsinInput.value,
            product_name: productNameInput.value,
            category: productCategoryInput.value || null,
            avg_selling_price: parseFloat(productAvgSellingPriceInput.value),
            cost_of_goods_sold: parseFloat(productCostOfGoodsSoldInput.value),
            initial_cvr_baseline: parseFloat(productInitialCvrBaselineInput.value)
        };

        const id = productIdInput.value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_BASE_URL}/products/${id}` : `${API_BASE_URL}/products/`;

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(productData)
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || `Failed to ${id ? 'update' : 'create'} product.`);
            }
            displayMessage(productMessage, `Product ${id ? 'updated' : 'created'} successfully: ${result.product_name || result.detail}`, false);
            clearProductForm();
            fetchProducts(); // Refresh list
        } catch (error) {
            displayMessage(productMessage, error.message, true);
        }
    });

    const deleteProduct = async (id) => {
        const token = getToken();
        if (!token) return;
        try {
            const response = await fetch(`${API_BASE_URL}/products/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json(); // Expects a message like {"detail": "..."}
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to delete product.');
            }
            displayMessage(productMessage, result.detail || `Product ID ${id} deleted successfully.`, false);
            fetchProducts(); // Refresh list
        } catch (error) {
            displayMessage(productMessage, error.message, true);
        }
    };

    clearFormButton.addEventListener('click', clearProductForm);
    refreshProductsButton.addEventListener('click', fetchProducts);

    // Initial fetch of products
    fetchProducts();
});
