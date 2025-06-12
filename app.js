// This is just a snippet! Only replace the renderTable function in your existing app.js

const renderTable = () => {
    tableBody.innerHTML = ''; // Clear existing rows
    if (!currentData || currentData.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5">No data available for this region. Check back later!</td></tr>';
        return;
    }

    currentData.forEach(ssd => {
        const row = document.createElement('tr');
        
        const formattedPrice = new Intl.NumberFormat(undefined, {
            style: 'currency',
            currency: ssd.currency,
        }).format(ssd.price);

        const formattedPricePerTb = new Intl.NumberFormat(undefined, {
            style: 'currency',
            currency: ssd.currency,
        }).format(ssd.price_per_tb);

        // This is the updated row structure with the image
        row.innerHTML = `
            <td><a href="${ssd.link}" target="_blank" rel="noopener sponsored"><img src="${ssd.image}" alt="${ssd.title}" class="product-image"></a></td>
            <td><a href="${ssd.link}" target="_blank" rel="noopener sponsored">${ssd.title}</a></td>
            <td>${ssd.capacity_gb} GB</td>
            <td>${formattedPrice}</td>
            <td>${formattedPricePerTb}</td>
        `;
        tableBody.appendChild(row);
    });
};