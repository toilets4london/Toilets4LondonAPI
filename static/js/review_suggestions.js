var map;
var marker;
var geocoder;
var listEl;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 11,
        center: {lat: 51.505, lng: -0.09},
    });
    geocoder = new google.maps.Geocoder();
    marker = null;

    // --- Build suggestion cards ---
    listEl = document.getElementById('suggestion-list');

    if (suggestions.length > 0) {
        listEl.innerHTML = '';
        suggestions.forEach(function (s) {
            var card = document.createElement('div');
            card.className = 'suggestion-card';
            card.id = 'card-' + s.id;
            card.innerHTML =
                '<div class="card-id">#' + s.id + '</div>' +
                '<div class="card-date">' + s.date + '</div>' +
                (s.details ? '<div class="card-details">' + escapeHtml(s.details) + '</div>' : '') +
                '<div class="card-coords">' + s.latitude.toFixed(5) + ', ' + s.longitude.toFixed(5) + '</div>';
            card.addEventListener('click', function () { selectSuggestion(s); });
            listEl.appendChild(card);
        });
    }
}

// --- Select a suggestion ---
function selectSuggestion(s) {
    // Highlight active card
    document.querySelectorAll('.suggestion-card').forEach(function (c) {
        c.classList.remove('active');
    });
    var card = document.getElementById('card-' + s.id);
    if (card) card.classList.add('active');

    // Move map
    var pos = {lat: s.latitude, lng: s.longitude};
    if (marker) {
        marker.setPosition(pos);
    } else {
        marker = new google.maps.Marker({
            map: map,
            position: pos,
        });
    }
    map.setCenter(pos);
    map.setZoom(16);

    // Populate form
    document.getElementById('form-suggestion-id').value = s.id;
    document.getElementById('form-latitude').value = s.latitude;
    document.getElementById('form-longitude').value = s.longitude;
    document.getElementById('form-name').value = '';
    document.getElementById('form-opening-hours').value = '';
    document.getElementById('form-wheelchair').checked = false;
    document.getElementById('form-baby-change').checked = false;
    document.getElementById('form-fee').value = 'Free';
    document.getElementById('form-data-source').value = 'App upload';
    document.getElementById('form-borough').value = '';

    // Show user details
    var detailsEl = document.getElementById('suggestion-details');
    detailsEl.textContent = s.details ? 'User note: ' + s.details : 'No details provided.';

    // Show form
    document.getElementById('approval-form').style.display = 'block';
    hideMessage();

    // Reverse geocode
    reverseGeocode(s.latitude, s.longitude);
}

// --- Reverse geocoding via Google Maps Geocoder ---
function reverseGeocode(lat, lng) {
    var addressField = document.getElementById('form-address');
    addressField.value = 'Loading address...';

    geocoder.geocode({location: {lat: lat, lng: lng}}, function (results, status) {
        if (status === 'OK' && results[0]) {
            addressField.value = results[0].formatted_address;
            autoSelectBorough(results[0].address_components);
        } else {
            addressField.value = '';
        }
    });
}

// --- Auto-detect borough from Google address components ---
function autoSelectBorough(components) {
    var boroughSelect = document.getElementById('form-borough');
    // Collect relevant locality names from Google's response
    var candidates = [];
    components.forEach(function (c) {
        if (c.types.indexOf('locality') !== -1 ||
            c.types.indexOf('sublocality') !== -1 ||
            c.types.indexOf('sublocality_level_1') !== -1 ||
            c.types.indexOf('neighborhood') !== -1 ||
            c.types.indexOf('postal_town') !== -1 ||
            c.types.indexOf('administrative_area_level_2') !== -1) {
            candidates.push(c.long_name);
        }
    });

    for (var i = 0; i < boroughSelect.options.length; i++) {
        var opt = boroughSelect.options[i];
        if (!opt.value) continue;
        var val = opt.value.toLowerCase();
        for (var j = 0; j < candidates.length; j++) {
            if (candidates[j].toLowerCase().indexOf(val) !== -1 || val.indexOf(candidates[j].toLowerCase()) !== -1) {
                boroughSelect.value = opt.value;
                return;
            }
        }
    }
}

// --- Approve ---
window.approveSuggestion = function () {
    var borough = document.getElementById('form-borough').value;
    if (!borough) {
        if (!confirm('No borough selected. Continue anyway?')) return;
    }

    var payload = {
        suggested_toilet_id: document.getElementById('form-suggestion-id').value,
        latitude: document.getElementById('form-latitude').value,
        longitude: document.getElementById('form-longitude').value,
        address: document.getElementById('form-address').value,
        name: document.getElementById('form-name').value,
        borough: borough,
        opening_hours: document.getElementById('form-opening-hours').value,
        wheelchair: document.getElementById('form-wheelchair').checked,
        baby_change: document.getElementById('form-baby-change').checked,
        fee: document.getElementById('form-fee').value,
        data_source: document.getElementById('form-data-source').value,
    };

    fetch('/review-suggestions/approve/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(payload),
    })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success) {
                removeCard(payload.suggested_toilet_id);
                showMessage('Toilet added successfully! (ID: ' + data.toilet_id + ')', 'success');
            } else {
                showMessage('Error: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(function (err) {
            showMessage('Network error: ' + err.message, 'error');
        });
};

// --- Dismiss ---
window.dismissSuggestion = function () {
    if (!confirm('Dismiss this suggestion? This cannot be undone.')) return;

    var id = document.getElementById('form-suggestion-id').value;

    fetch('/review-suggestions/dismiss/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({suggested_toilet_id: id}),
    })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success) {
                removeCard(id);
                showMessage('Suggestion dismissed.', 'info');
            } else {
                showMessage('Error: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(function (err) {
            showMessage('Network error: ' + err.message, 'error');
        });
};

// --- Helpers ---
function removeCard(id) {
    var card = document.getElementById('card-' + id);
    if (card) card.remove();
    document.getElementById('approval-form').style.display = 'none';
    if (marker) {
        marker.setMap(null);
        marker = null;
    }

    // Update count in sidebar
    var remaining = document.querySelectorAll('.suggestion-card').length;
    document.querySelector('.sidebar h2').textContent = 'Suggestions (' + remaining + ')';
    if (remaining === 0) {
        listEl.innerHTML = '<div class="empty-state">No pending suggestions to review.</div>';
    }
}

function getCsrfToken() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
}

function showMessage(text, type) {
    var bar = document.getElementById('message-bar');
    bar.textContent = text;
    bar.className = 'message-bar ' + type;
    bar.style.display = 'block';
}

function hideMessage() {
    document.getElementById('message-bar').style.display = 'none';
}

function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}
