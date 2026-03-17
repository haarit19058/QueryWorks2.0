
import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { GEOAPIFY_API_KEY } from '../constants';

interface MapComponentProps {
  source?: [number, number];
  destination?: [number, number];
  onMapClick?: (lat: number, lng: number) => void;
}

export const MapComponent: React.FC<MapComponentProps> = ({ source, destination, onMapClick }) => {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const polylineRef = useRef<L.Polyline | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    mapRef.current = L.map(containerRef.current).setView([23.2127, 72.6845], 13);

    L.tileLayer(`https://maps.geoapify.com/v1/tile/osm-bright/{z}/{x}/{y}.png?apiKey=${GEOAPIFY_API_KEY}`, {
      attribution: 'Powered by <a href="https://www.geoapify.com/" target="_blank">Geoapify</a> | <a href="https://openmaptiles.org/" target="_blank">© OpenMapTiles</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap</a> contributors',
      maxZoom: 20,
    }).addTo(mapRef.current);

    if (onMapClick) {
      mapRef.current.on('click', (e) => {
        onMapClick(e.latlng.lat, e.latlng.lng);
      });
    }

    // Fix for "gray map" issue when container is dynamic
    const resizeObserver = new ResizeObserver(() => {
      mapRef.current?.invalidateSize();
    });
    resizeObserver.observe(containerRef.current);

    // Initial check
    setTimeout(() => {
      mapRef.current?.invalidateSize();
    }, 250);

    return () => {
      resizeObserver.disconnect();
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [onMapClick]);

  useEffect(() => {
    if (!mapRef.current) return;

    // Clear old markers and polyline
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];
    if (polylineRef.current) {
      polylineRef.current.remove();
      polylineRef.current = null;
    }

    const points: L.LatLngExpression[] = [];

    if (source) {
      const marker = L.marker(source, {
        icon: L.icon({
          iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
          iconSize: [32, 32],
          iconAnchor: [16, 32]
        })
      }).addTo(mapRef.current);
      markersRef.current.push(marker);
      points.push(source);
    }

    if (destination) {
      const marker = L.marker(destination, {
        icon: L.icon({
          iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
          iconSize: [32, 32],
          iconAnchor: [16, 32]
        })
      }).addTo(mapRef.current).bindPopup('Destination').openPopup();
      markersRef.current.push(marker);
      points.push(destination);
    }

    if (source && destination) {
      const polyline = L.polyline([source, destination], {
        color: '#10B981',
        weight: 4,
        opacity: 0.7,
        dashArray: '10, 10'
      }).addTo(mapRef.current);
      polylineRef.current = polyline;
      mapRef.current.fitBounds(polyline.getBounds(), { padding: [50, 50] });
    } else if (points.length > 0) {
      mapRef.current.setView(points[0], 15);
    }
  }, [source, destination]);

  return <div ref={containerRef} className="w-full h-full min-h-[400px]" />;
};
