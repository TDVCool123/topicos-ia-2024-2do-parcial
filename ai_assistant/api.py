from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query
from llama_index.core.agent import ReActAgent
from ai_assistant.agent import TravelAgent
from ai_assistant.models import AgentAPIResponse, RestaurantReservation, TripReservation, HotelReservation
from ai_assistant.tools import reserve_hotel,reserve_bus,reserve_flight,reserve_restaurant, create_trip_report_tool


AVAILABLE_DEPARTMENTS = [
    "La Paz", "Santa Cruz", "Cochabamba", "Sucre", 
    "Potosí", "Oruro", "Tarija", "Beni", "Pando"
]


def get_agent() -> ReActAgent:
    return TravelAgent().get_agent()


app = FastAPI(title="AI Agent")


@app.get("/recommendations/DEPARTMENTS")
def recommend_DEPARTMENTS(
    notes: list[str] = Query(...), agent: ReActAgent = Depends(get_agent)
):
    prompt = f"recommend DEPARTMENTS in bolivia with the following notes: {notes}"
    result = AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

    return result.agent_response


# Recomendación de lugares según la ciudad
@app.get("/recommendations/places")
def recommend_places(
    department: str = Query(..., description="Select a department", enum=AVAILABLE_DEPARTMENTS),
    notes: Optional[List[str]] = Query(None), 
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"recommend places to visit in {department}"
    if notes:
        prompt += f" with the following notes: {notes}"
    result = AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

    return result.agent_response

# Recomendación de hoteles según la ciudad
@app.get("/recommendations/hotels")
def recommend_hotels(
    department: str = Query(..., description="Select a department", enum=AVAILABLE_DEPARTMENTS),
    notes: Optional[List[str]] = Query(None), 
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"recommend hotels in {department}"
    if notes:
        prompt += f" with the following notes: {notes}"
    result = AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

    return result.agent_response

# Recomendación de actividades según la ciudad
@app.get("/recommendations/activities")
def recommend_activities(
    department: str = Query(..., description="Select a department", enum=AVAILABLE_DEPARTMENTS),
    notes: Optional[List[str]] = Query(None), 
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"recommend activities in {department}"
    if notes:
        prompt += f" with the following notes: {notes}"
    result = AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

    return result.agent_response



##POST

# Reservar vuelo
@app.post("/reservations/flight")
def make_flight_reservation(
    date_str: str, 
    departure: str, 
    destination: str, 
    cost: int
):
    try:
        reservation: TripReservation = reserve_flight(date_str, departure, destination, cost)
        return {"status": "Reservation made", "reservation": reservation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Reservar bus
@app.post("/reservations/bus")
def make_bus_reservation(
    date_str: str, 
    departure: str, 
    destination: str, 
    cost: int
):
    try:
        reservation: TripReservation = reserve_bus(date_str, departure, destination, cost)
        return {"status": "Reservation made", "reservation": reservation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Reservar hotel
@app.post("/reservations/hotel")
def make_hotel_reservation(
    date_start_str: str, 
    date_end_str: str, 
    hotel: str, 
    department: str, 
    cost: int
):
    try:
        reservation: HotelReservation = reserve_hotel(date_start_str, date_end_str, hotel, department, cost)
        return {"status": "Reservation made", "reservation": reservation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Reservar restaurante
@app.post("/reservations/restaurant")
def make_restaurant_reservation(
    date_str: str, 
    time_str: str, 
    restaurant: str, 
    department: str, 
    dish: str,  
    cost: int
):
    try:
        reservation: RestaurantReservation = reserve_restaurant(date_str, time_str, restaurant, department, dish, cost)
        return {"status": "Reservation made", "reservation": reservation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/trip/report")
def get_trip_report(
    file_path = "trip.json", agent: ReActAgent = Depends(get_agent)
):
    prompt = f"Create a report from the {file_path} file"
    trip_report = AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

    return trip_report