/**
 * Persons Page JavaScript
 */

let allPersons = [];

document.addEventListener('DOMContentLoaded', async function() {
    await loadPersons();
    initializeSearch();
    initializeModal();
});

/**
 * Load all persons
 */
async function loadPersons() {
    try {
        Utils.showLoading('personsGrid');

        allPersons = await api.getPersons();

        displayPersons(allPersons);

    } catch (error) {
        Utils.handleError(error, 'loading persons');
        document.getElementById('personsGrid').innerHTML =
            '<div class="loading-spinner">Error loading persons</div>';
    }
}

/**
 * Display persons grid
 */
function displayPersons(persons) {
    const grid = document.getElementById('personsGrid');

    if (!persons || persons.length === 0) {
        grid.innerHTML = '<div class="loading-spinner">No registered persons found</div>';
        return;
    }

    grid.innerHTML = persons.map(person => `
        <div class="person-card" data-id="${person.id}">
            <img src="${person.profile_image ? `http://localhost:8000/static/${person.profile_image}` : 'https://via.placeholder.com/300x200?text=No+Image'}"
                 alt="${person.name}"
                 class="person-image"
                 onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
            <div class="person-info">
                <div class="person-name">${person.name}</div>
                ${person.employee_id ? `<div class="person-details">ID: ${person.employee_id}</div>` : ''}
                ${person.email ? `<div class="person-details">Email: ${person.email}</div>` : ''}
                ${person.department ? `<div class="person-details">Dept: ${person.department}</div>` : ''}
                ${person.last_seen ? `<div class="person-details">Last seen: ${Utils.formatRelativeTime(person.last_seen)}</div>` : ''}

                <div class="person-actions">
                    <button class="btn btn-primary btn-sm" onclick="viewPerson(${person.id})">
                        View Details
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="editPerson(${person.id})">
                        Edit
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deletePerson(${person.id}, '${person.name}')">
                        Delete
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Initialize search
 */
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');

    searchInput.addEventListener('input', Utils.debounce(function(e) {
        const query = e.target.value.toLowerCase().trim();

        if (!query) {
            displayPersons(allPersons);
            return;
        }

        const filtered = allPersons.filter(person => {
            return person.name.toLowerCase().includes(query) ||
                   (person.email && person.email.toLowerCase().includes(query)) ||
                   (person.employee_id && person.employee_id.toLowerCase().includes(query)) ||
                   (person.department && person.department.toLowerCase().includes(query));
        });

        displayPersons(filtered);
    }, 300));
}

/**
 * View person details
 */
async function viewPerson(personId) {
    try {
        const person = await api.getPerson(personId);

        const modal = document.getElementById('personModal');
        const detailContainer = document.getElementById('personDetail');

        detailContainer.innerHTML = `
            <h2>${person.name}</h2>
            <img src="${person.profile_image ? `http://localhost:8000/static/${person.profile_image}` : 'https://via.placeholder.com/400x300?text=No+Image'}"
                 alt="${person.name}"
                 style="width: 100%; max-width: 400px; border-radius: 8px; margin: 1rem 0;"
                 onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">

            <div style="margin: 1rem 0;">
                <strong>Employee ID:</strong> ${person.employee_id || 'N/A'}<br>
                <strong>Email:</strong> ${person.email || 'N/A'}<br>
                <strong>Phone:</strong> ${person.phone || 'N/A'}<br>
                <strong>Department:</strong> ${person.department || 'N/A'}<br>
                <strong>Designation:</strong> ${person.designation || 'N/A'}<br>
                <strong>Registered:</strong> ${Utils.formatDateTime(person.registration_date)}<br>
                <strong>Last Seen:</strong> ${person.last_seen ? Utils.formatDateTime(person.last_seen) : 'Never'}<br>
                <strong>Status:</strong> ${person.is_active ? '<span style="color: var(--success-color);">Active</span>' : '<span style="color: var(--danger-color);">Inactive</span>'}
            </div>

            ${person.notes ? `
                <div style="margin: 1rem 0;">
                    <strong>Notes:</strong><br>
                    <p>${person.notes}</p>
                </div>
            ` : ''}

            <div style="margin-top: 1.5rem;">
                <button class="btn btn-danger" onclick="deletePerson(${person.id}, '${person.name}'); closeModal();">
                    Delete Person
                </button>
            </div>
        `;

        modal.style.display = 'flex';
        console.log('Modal opened');

    } catch (error) {
        Utils.handleError(error, 'loading person details');
    }
}

/**
 * Delete person
 */
async function deletePerson(personId, personName) {
    if (!Utils.confirm(`Are you sure you want to delete ${personName}?`)) {
        return;
    }

    try {
        await api.deletePerson(personId);

        Utils.showMessage(`${personName} has been deleted`, 'success');

        // Reload persons list
        await loadPersons();

    } catch (error) {
        Utils.handleError(error, 'deleting person');
    }
}

/**
 * Initialize modal
 */
function initializeModal() {
    const modal = document.getElementById('personModal');
    const closeBtn = modal.querySelector('.modal-close');

    // Close button click
    closeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        closeModal();
    });

    // Close on outside click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display !== 'none') {
            closeModal();
        }
    });

    console.log('Modal initialized with close handlers');
}

/**
 * Close modal
 */
function closeModal() {
    const modal = document.getElementById('personModal');
    modal.style.display = 'none';
    console.log('Modal closed');
}

/**
 * Edit person details
 */
async function editPerson(personId) {
    try {
        const person = await api.getPerson(personId);

        const modal = document.getElementById('personModal');
        const detailContainer = document.getElementById('personDetail');

        detailContainer.innerHTML = `
            <h2>Edit Person</h2>
            <form id="editPersonForm" style="margin-top: 1rem;">
                <div class="form-group">
                    <label for="editName">Full Name *</label>
                    <input type="text" id="editName" name="name" value="${person.name}" required class="form-control">
                </div>

                <div class="form-group">
                    <label for="editEmail">Email</label>
                    <input type="email" id="editEmail" name="email" value="${person.email || ''}" class="form-control">
                </div>

                <div class="form-group">
                    <label for="editEmployeeId">Employee ID</label>
                    <input type="text" id="editEmployeeId" name="employee_id" value="${person.employee_id || ''}" class="form-control">
                </div>

                <div class="form-group">
                    <label for="editPhone">Phone</label>
                    <input type="tel" id="editPhone" name="phone" value="${person.phone || ''}" class="form-control">
                </div>

                <div class="form-group">
                    <label for="editDepartment">Department</label>
                    <input type="text" id="editDepartment" name="department" value="${person.department || ''}" class="form-control">
                </div>

                <div class="form-group">
                    <label for="editDesignation">Designation</label>
                    <input type="text" id="editDesignation" name="designation" value="${person.designation || ''}" class="form-control">
                </div>

                <div class="form-group">
                    <label for="editNotes">Notes</label>
                    <textarea id="editNotes" name="notes" rows="3" class="form-control">${person.notes || ''}</textarea>
                </div>

                <div style="margin-top: 1.5rem; display: flex; gap: 1rem;">
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                </div>
            </form>
        `;

        // Handle form submission
        document.getElementById('editPersonForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await updatePerson(personId, e.target);
        });

        modal.style.display = 'flex';

    } catch (error) {
        Utils.handleError(error, 'loading person details for editing');
    }
}

/**
 * Update person details
 */
async function updatePerson(personId, form) {
    try {
        const formData = {
            name: form.name.value,
            email: form.email.value || null,
            employee_id: form.employee_id.value || null,
            phone: form.phone.value || null,
            department: form.department.value || null,
            designation: form.designation.value || null,
            notes: form.notes.value || null
        };

        await api.put(`/api/persons/${personId}`, formData);

        Utils.showMessage('Person updated successfully', 'success');
        closeModal();
        await loadPersons();

    } catch (error) {
        Utils.handleError(error, 'updating person');
    }
}

// Make functions global for onclick handlers
window.viewPerson = viewPerson;
window.editPerson = editPerson;
window.deletePerson = deletePerson;
window.closeModal = closeModal;
