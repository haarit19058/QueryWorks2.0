
export type User = {
  id: string;
  name: string;
  email: string;
  profilePic: string;
  gender: string;
  age: number
};

export enum RideStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed'
}

export type Ride = {
  id: string;
  creatorId: string;
  sourceName: string;
  sourceLat: number;
  sourceLng: number;
  destName: string;
  destLat: number;
  destLng: number;
  departureTime: string;
  totalSeats: number;
  seatsAvailable: number;
  status: RideStatus;
};

export enum RequestStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected'
}

export type JoinRequest = {
  id: string;
  rideId: string;
  userId: string;
  userName: string;
  status: RequestStatus;
};

export type ChatMessage = {
  id: string;
  rideId: string;
  senderId: string;
  senderName: string;
  message: string;
  timestamp: string;
};

export interface GeoLocation {
  lat: number;
  lon: number;
  display_name: string;
}
