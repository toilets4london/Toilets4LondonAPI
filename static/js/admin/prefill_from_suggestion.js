/**
 * When the toilet add form is opened from a suggested toilet
 * (?from_suggestion=1&latitude=..&longitude=..), prefill the address
 * (via Google reverse geocoding) and the borough (via postcodes.io).
 * Both are left blank if the lookup fails.
 */
(function () {

    var params = new URLSearchParams(window.location.search);

    if (params.get('from_suggestion') !== '1') {
        return;
    }

    var lat = parseFloat(params.get('latitude'));
    var lng = parseFloat(params.get('longitude'));

    if (isNaN(lat) || isNaN(lng)) {
        return;
    }

    function prefillAddress() {
        var addressInput = document.getElementById('id_address');
        if (!addressInput || addressInput.value) {
            return;
        }
        if (typeof google === 'undefined' || !google.maps) {
            return;
        }
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({location: {lat: lat, lng: lng}}, function (results, status) {
            if (status === 'OK' && results[0] && !addressInput.value) {
                addressInput.value = results[0].formatted_address
                    .replace(/, London, UK$/, '')
                    .replace(/, London$/, '')
                    .replace(/, UK$/, '');
            }
        });
    }

    function prefillBorough() {
        var boroughSelect = document.getElementById('id_borough');
        if (!boroughSelect || boroughSelect.value) {
            return;
        }
        fetch('https://api.postcodes.io/postcodes?lon=' + lng + '&lat=' + lat + '&limit=1')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.result && data.result.length > 0) {
                    var district = data.result[0].admin_district;
                    if (district && !boroughSelect.value) {
                        for (var i = 0; i < boroughSelect.options.length; i++) {
                            if (boroughSelect.options[i].value === district) {
                                boroughSelect.value = district;
                                return;
                            }
                        }
                    }
                }
            })
            .catch(function () {
                // Leave borough blank if lookup fails
            });
    }

    document.addEventListener('DOMContentLoaded', function () {
        prefillAddress();
        prefillBorough();
    });

})();
