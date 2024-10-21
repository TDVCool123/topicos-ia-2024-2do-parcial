from random import randint
from datetime import date, datetime, time
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from ai_assistant.rags import TravelGuideRAG
from ai_assistant.prompts import travel_guide_qa_tpl, travel_guide_description
from ai_assistant.config import get_agent_settings
from ai_assistant.models import (
    TripReservation,
    TripType,
    HotelReservation,
    RestaurantReservation,
)
from ai_assistant.utils import save_reservation

SETTINGS = get_agent_settings()

travel_guide_tool = QueryEngineTool(
    query_engine=TravelGuideRAG(
        store_path=SETTINGS.travel_guide_store_path,
        data_dir=SETTINGS.travel_guide_data_path,
        qa_prompt_tpl=travel_guide_qa_tpl,
    ).get_query_engine(),
    metadata=ToolMetadata(
        name="travel_guide", description=travel_guide_description, return_direct=False
    ),
)




# Tool functions
def reserve_flight(date_str: str, departure: str, destination: str, cost: int) -> TripReservation:
    """
    Ensure the reservation date is in the future.
    """
    print(
        f"Making flight reservation from {departure} to {destination} on date: {date} with {cost} bolivianos"
    )
    current_date = date.today()
    reserve_date = date.fromisoformat(date_str)

    if reserve_date > current_date:
        reservation = TripReservation(
            trip_type=TripType.flight,
            departure=departure,
            destination=destination,
            date=reserve_date,
            cost=randint(200,10000)
        )
        save_reservation(reservation)
        return reservation
    else:
        return "Please provide a valid future date for the flight."

def reserve_bus(date_str: str, departure: str, destination: str, cost: int) -> TripReservation:
    """
    Ensure the reservation date is in the future.
    """
    print(
        f"Making bus reservation from {departure} to {destination} on date: {date} with {cost} bolivianos"
    )
    current_date=date.today()
    reserve_date=date.fromisoformat(date_str)

    if reserve_date > current_date:
        reservation = TripReservation(
            trip_type=TripType.bus,
            departure=departure,
            destination=destination,
            date=reserve_date,
            cost=randint(2,10)
        )
        save_reservation(reservation)
        return reservation
    else:
        return "Please provide a valid future date for the bus trip."


def reserve_hotel(date_start_str: str, date_end_str: str, hotel: str, department: str, cost: int) -> HotelReservation:
    """
    Check if the date is higher than today

    """
    print(
        f"Making hotel reservation since {date_start_str} until {date_end_str} in the hotel {hotel} in {department} with {cost} bolivianos"
    )
    current_date=date.today()
    checkin_date =date.fromisoformat(date_start_str)
    checkout_date =date.fromisoformat(date_end_str)

    if checkin_date  > current_date:
        if checkout_date > checkin_date :
            reservation = HotelReservation(
                checkin_date=checkin_date ,
                checkout_date=checkout_date,
                city=department,
                hotel_name=hotel,
                cost=randint(50,500)
            )
            save_reservation(reservation)
            return reservation
        else:
            return "Please provide a valid checkout date (after check-in date)."
    else:
        return "Please provide a valid check-in date (in the future)."


def reserve_restaurant(date_str: str, time_str: str, restaurant: str, department: str, dish: str,  cost: int) -> RestaurantReservation:
    """
    Combining date and time
    Ensure the reservation date and time are valid and in the future.
    """
    print(
        f"Making restaurant reservation in {restaurant} in {department} on date {date_str} at {time} asking for a {dish} with {cost} bolivianos"
    )
    current_datetime=datetime.now()
    # Combining date and time into a single datetime object
    try:
        reserve_datetime = datetime.fromisoformat(f"{date_str}T{time_str}")
    except ValueError:
        return "Please provide a valid date and time in the correct format (YYYY-MM-DD for date and HH:MM for time)."


    if reserve_datetime > current_datetime:
        # Create the reservation
        reservation = RestaurantReservation(
            reservation_time=reserve_datetime,
            restaurant=restaurant,
            city=department,
            dish=dish,
            cost=cost
        )
        save_reservation(reservation)
        return reservation
    else:
        return "Please provide a valid future date and time for the reservation."
    

import json
from datetime import datetime
from typing import List, Dict, Any

def create_trip_report_tool(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r') as f:
        reservations = json.load(f)
    
    def get_reservation_date(reservation: Dict[str, Any]) -> datetime:
        if reservation['reservation_type'] == 'TripReservation':
            return datetime.strptime(reservation['date'], "%Y-%m-%d")
        elif reservation['reservation_type'] == 'HotelReservation':
            return datetime.strptime(reservation['checkin_date'], "%Y-%m-%d")
        elif reservation['reservation_type'] == 'RestaurantReservation':
            return datetime.strptime(reservation['reservation_time'], "%Y-%m-%dT%H:%M:%S")
        return None

    # Ordenar las reservas por fecha
    reservations.sort(key=get_reservation_date)

    trip_report = {
        "actividades": [],
        "total": 0,
        "lista_de_actividades": []
    }

    # Calcular el total y agregar detalles a la lista de actividades
    for reservation in reservations:
        if reservation['reservation_type'] == 'TripReservation':
            activity_name = f"Flight from {reservation['departure']} to {reservation['destination']}"
            activity_date = reservation['date']
        elif reservation['reservation_type'] == 'HotelReservation':
            activity_name = f"Hotel stay at {reservation['hotel_name']} in {reservation['city']}"
            activity_date = reservation['checkin_date']
        elif reservation['reservation_type'] == 'RestaurantReservation':
            activity_name = f"Restaurant reservation at {reservation['restaurant']} in {reservation['city']}"
            activity_date = reservation['reservation_time']
        
        comments = reservation.get("comments", "No additional comments")

        trip_report["actividades"].append({
            "nombre_actividad": activity_name,
            "comentario": comments,
            "fecha": activity_date
        })

        trip_report["total"] += reservation['cost']

        trip_report["lista_de_actividades"].append(activity_name)

    return trip_report




flight_tool = FunctionTool.from_defaults(fn=reserve_flight, return_direct=False)
bus_tool = FunctionTool.from_defaults(fn=reserve_bus, return_direct=False)
hotel_tool = FunctionTool.from_defaults(fn=reserve_hotel, return_direct=False)
restaurant_tool = FunctionTool.from_defaults(fn=reserve_restaurant, return_direct=False)
trip_tool = FunctionTool.from_defaults(fn=create_trip_report_tool, return_direct=False)