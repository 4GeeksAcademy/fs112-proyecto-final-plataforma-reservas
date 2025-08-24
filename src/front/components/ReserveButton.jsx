import React from "react";
import { Link } from "react-router-dom";

<button
  type="button"
  className="btn btn-primary"
  onClick={async () => {
    const fecha = new Date().toISOString().slice(0, 10);
    const payload = {
      spaceId: "AULA-101",
      userId: "USER-123",
      start: fecha + "T" + "09:00" + ":00",
      end: fecha + "T" + "10:00" + ":00"
    };
    await fetch("http://localhost:3000/reservations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  }}
>
  Reservar
</button>

