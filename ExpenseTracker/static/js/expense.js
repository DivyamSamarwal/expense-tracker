// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Handle edit expense modal
    const editButtons = document.querySelectorAll('.edit-btn');
    const editForm = document.getElementById('editExpenseForm');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get expense data from data attributes
            const id = this.getAttribute('data-id');
            const amount = this.getAttribute('data-amount');
            const category = this.getAttribute('data-category');
            const date = this.getAttribute('data-date');
            const description = this.getAttribute('data-description');
            
            // Set form action
            editForm.action = `/edit_expense/${id}`;
            
            // Populate form fields
            document.getElementById('edit_amount').value = amount;
            document.getElementById('edit_category').value = category;
            document.getElementById('edit_date').value = date;
            document.getElementById('edit_description').value = description;
        });
    });
    
    // Handle delete expense modal
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const deleteForm = document.getElementById('deleteExpenseForm');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            deleteForm.action = `/delete_expense/${id}`;
        });
    });

    // Set today's date as default for new expense form
    const dateInput = document.querySelector('input[name="date"]');
    if (dateInput && !dateInput.value) {
        const today = new Date();
        const yyyy = today.getFullYear();
        let mm = today.getMonth() + 1; // Months start at 0
        let dd = today.getDate();

        if (dd < 10) dd = '0' + dd;
        if (mm < 10) mm = '0' + mm;

        const formattedToday = yyyy + '-' + mm + '-' + dd;
        dateInput.value = formattedToday;
    }
});
