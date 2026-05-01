from vehicle import add_vehicle, remove_vehicle
from parking_slot import add_slot, occupy_slot, free_slot, get_available_slots
from payment_system import add_payment, calculate_fee

def park_vehicle(vehicle_number, vehicle_type, slot_number):
    vehicle_id = add_vehicle(vehicle_number, vehicle_type)
    available_slots = get_available_slots()
    slot = next((s for s in available_slots if s[0] == int(slot_number)), None)
    if slot:
        occupy_slot(slot[0])
        print(f"Vehicle parked in slot {slot_number}.")
        return vehicle_id
    else:
        print("No available slot with this number!")
        remove_vehicle(vehicle_id)
        return None

def remove_parked_vehicle(vehicle_id, hours_parked):
    fee = calculate_fee(hours_parked)
    add_payment(vehicle_id, fee)
    # Free the slot (assuming slot_id = vehicle_id for simplicity)
    free_slot(vehicle_id)
    remove_vehicle(vehicle_id)
    print(f"Vehicle {vehicle_id} removed. Fee: {fee}")
