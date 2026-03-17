
import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import { fileURLToPath } from "url";
import { Sequelize, DataTypes, Model } from "sequelize";
import cors from "cors";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize Sequelize with MySQL
const sequelize = new Sequelize(
  process.env.MYSQL_DATABASE || "iitgn_pool",
  process.env.MYSQL_USER || "root",
  process.env.MYSQL_PASSWORD || "",
  {
    host: process.env.MYSQL_HOST || "localhost",
    port: parseInt(process.env.MYSQL_PORT || "3306"),
    dialect: "mysql",
    logging: false,
  }
);

// Define Models
class User extends Model {}
User.init({
  id: { type: DataTypes.STRING, primaryKey: true },
  name: DataTypes.STRING,
  email: DataTypes.STRING,
  profilePic: DataTypes.STRING,
}, { sequelize, modelName: 'user' });

class Ride extends Model {}
Ride.init({
  id: { type: DataTypes.STRING, primaryKey: true },
  creatorId: DataTypes.STRING,
  sourceName: DataTypes.STRING,
  sourceLat: DataTypes.FLOAT,
  sourceLng: DataTypes.FLOAT,
  destName: DataTypes.STRING,
  destLat: DataTypes.FLOAT,
  destLng: DataTypes.FLOAT,
  departureTime: DataTypes.STRING,
  totalSeats: DataTypes.INTEGER,
  seatsAvailable: DataTypes.INTEGER,
  status: { type: DataTypes.ENUM('active', 'completed'), defaultValue: 'active' },
}, { sequelize, modelName: 'ride' });

class JoinRequest extends Model {}
JoinRequest.init({
  id: { type: DataTypes.STRING, primaryKey: true },
  rideId: DataTypes.STRING,
  userId: DataTypes.STRING,
  userName: DataTypes.STRING,
  status: { type: DataTypes.ENUM('pending', 'approved', 'rejected'), defaultValue: 'pending' },
}, { sequelize, modelName: 'join_request' });

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(cors());
  app.use(express.json());

  // Sync Database
  try {
    await sequelize.authenticate();
    console.log('Connection to MySQL has been established successfully.');
    await sequelize.sync();
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }

  // API Routes
  app.get("/api/rides", async (req, res) => {
    const rides = await Ride.findAll({ order: [['createdAt', 'DESC']] });
    res.json(rides);
  });

  app.post("/api/rides", async (req, res) => {
    const ride = await Ride.create({
      ...req.body,
      id: Math.random().toString(36).substr(2, 9),
      status: 'active'
    });
    res.json(ride);
  });

  app.patch("/api/rides/:id/status", async (req, res) => {
    const { id } = req.params;
    const { status } = req.body;
    await Ride.update({ status }, { where: { id } });
    res.json({ success: true });
  });

  app.get("/api/requests", async (req, res) => {
    const requests = await JoinRequest.findAll();
    res.json(requests);
  });

  app.post("/api/requests", async (req, res) => {
    const request = await JoinRequest.create({
      ...req.body,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending'
    });
    res.json(request);
  });

  app.patch("/api/requests/:id", async (req, res) => {
    const { id } = req.params;
    const { status } = req.body;
    const request = await JoinRequest.findByPk(id);
    if (request && status === 'approved') {
      const ride = await Ride.findByPk(request.get('rideId') as string);
      if (ride && (ride.get('seatsAvailable') as number) > 0) {
        await Ride.update(
          { seatsAvailable: (ride.get('seatsAvailable') as number) - 1 },
          { where: { id: request.get('rideId') as string } }
        );
      }
    }
    await JoinRequest.update({ status }, { where: { id } });
    res.json({ success: true });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
