window.onload = init;

function init(){
    const autmap = L.map('mapid',{
        center: [47.6964, 13.3458],
        zoom: 7,
        minZoom: 7,
        layers: [
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
	        attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'
            })
        ]
    })
}