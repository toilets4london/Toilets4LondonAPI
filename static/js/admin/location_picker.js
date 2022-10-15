/**
 * Create a map with a marker.
 * Creating or dragging the marker sets the latitude and longitude values
 * in the input fields.
 */
;(function ($) {

    const prev_el_selector = '.form-row.field-longitude';

    var initial_lat = 51.516448;
    var initial_lon = -0.130463;

    var initial_zoom = 10;

    const initial_with_loc_zoom = 16;

    var map;
    var marker;

    /**
     * Create HTML elements, display map, set up event listeners.
     */
    function initMap() {
        const lat_input = document.getElementById("id_latitude");
        const lon_input = document.getElementById("id_longitude");
        const $prevEl = $(prev_el_selector);

        if ($prevEl.length === 0) {
            return;
        }

        const has_initial_loc = (lat_input.value && lon_input.value);

        if (has_initial_loc) {
            initial_lat = parseFloat(lat_input.value);
            initial_lon = parseFloat(lon_input.value);
            initial_zoom = initial_with_loc_zoom;
        }

        $prevEl.after($('<div class="js-setloc-map setloc-map"></div>'));
        $prevEl.after($('<input id="pac-input" class="controls" type="text" placeholder="Search for a location..."/>'))

        var mapEl = document.getElementsByClassName('js-setloc-map')[0];

        map = new google.maps.Map(mapEl, {
            zoom: initial_zoom,
            center: {lat: initial_lat, lng: initial_lon}
        });

        const input = document.getElementById("pac-input");
        const searchBox = new google.maps.places.SearchBox(input);
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

        map.addListener("bounds_changed", () => {
            searchBox.setBounds(map.getBounds());
        });

        searchBox.addListener("places_changed", () => {
            map.setZoom(13);
            const places = searchBox.getPlaces();
            const bounds = new google.maps.LatLngBounds();
            const place = places[0];
            if (place.geometry.viewport) {
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
            map.fitBounds(bounds);
        });

        marker = new google.maps.Marker({
            map: map,
            draggable: true,
        });

        if (has_initial_loc) {
            setMarkerPosition(initial_lat, initial_lon);
        }

        map.addListener('click', (e) => {
            setMarkerPosition(e.latLng.lat(), e.latLng.lng());
        });

        marker.addListener('dragend', () => {
            setInputValues(marker.getPosition().lat(), marker.getPosition().lng());
        });

        lat_input.addEventListener('change', () => {
            marker.setPosition({lat: parseFloat(lat_input.value), lng: parseFloat(lon_input.value)});
            map.setCenter({lat: parseFloat(lat_input.value), lng: parseFloat(lon_input.value)});
        })

        lon_input.addEventListener('change', () => {
            marker.setPosition({lat: parseFloat(lat_input.value), lng: parseFloat(lon_input.value)});
            map.setCenter({lat: parseFloat(lat_input.value), lng: parseFloat(lon_input.value)});
        })

        function setMarkerPosition(lat, lon) {
            marker.setPosition({lat: lat, lng: lon});
            setInputValues(lat, lon);
        }

        function setInputValues(lat, lon) {
            lat_input.value = lat.toFixed(6);
            lon_input.value = lon.toFixed(6);
        }

    }

    $(document).ready(function () {
        initMap();
    });

})(django.jQuery);