
export const COLORS = {
  NAVY: '#0F172A',
  SLATE: '#64748B',
  ACCENT: '#10B981',
};

export const GEOAPIFY_API_KEY = '3e2fb214330c408f8a9c2c52e3f42579'; // Demo key for geocoding

export const INITIAL_RIDES = [
  {
    id: '1',
    creatorId: 'user1',
    sourceName: 'IITGN Housing Block',
    sourceLat: 23.2127,
    sourceLng: 72.6845,
    destName: 'Ahmedabad Airport (AMD)',
    destLat: 23.0734,
    destLng: 72.6266,
    departureTime: '2023-11-20T10:00',
    totalSeats: 4,
    seatsAvailable: 2,
    status: 'active'
  },
  {
    id: '2',
    creatorId: 'user2',
    sourceName: 'IITGN Academic Block',
    sourceLat: 23.2100,
    sourceLng: 72.6850,
    destName: 'Motera Stadium Metro',
    destLat: 23.0906,
    destLng: 72.6017,
    departureTime: '2023-11-20T18:30',
    totalSeats: 3,
    seatsAvailable: 3,
    status: 'active'
  }
];
