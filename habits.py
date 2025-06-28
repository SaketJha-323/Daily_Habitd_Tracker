from fastapi import APIRouter, Depends, HTTPException
from db import db
from datetime import date, timedelta
from auth import get_current_user
from models import HabitCreate

router = APIRouter()

@router.post("/habits")
async def create_habit(habit: HabitCreate, user=Depends(get_current_user)):
    doc = {
        "user_id": user["_id"],
        "name": habit.name,
        "goal_days": habit.goal_days,
        "completions": []
    }
    await db.habits.insert_one(doc)
    return {"msg": "Habit created"}

@router.post("/habits/{habit_name}/complete")
async def complete_habit(habit_name: str, user=Depends(get_current_user)):
    today = date.today().isoformat()
    habit = await db.habits.find_one({"user_id": user["_id"], "name": habit_name})
    if not habit:
        raise HTTPException(404, "Habit not found")
    if today in habit["completions"]:
        return {"msg": "Already marked"}
    await db.habits.update_one(
        {"_id": habit["_id"]},
        {"$addToSet": {"completions": today}}
    )
    return {"msg": "Marked complete"}

@router.get("/habits")
async def get_habits(user=Depends(get_current_user)):
    today = date.today()
    habits = await db.habits.find({"user_id": user["_id"]}).to_list(100)
    results = []
    for h in habits:
        completions = [date.fromisoformat(d) for d in h["completions"]]
        completions.sort()
        streak = 0
        for i in range(len(completions)-1, -1, -1):
            if completions[i] == today - timedelta(days=(len(completions)-1-i)):
                streak += 1
            else:
                break
        if completions:
            total_days = (today - completions[0]).days + 1
        else:
            total_days = 1
        consistency = (len(completions) / total_days) * 100
        results.append({
            "name": h["name"],
            "goal_days": h["goal_days"],
            "completed": len(completions),
            "streak": streak,
            "consistency": round(consistency, 2)
        })
    return results

@router.get("/habits/history")
async def habit_history(start: str, end: str, user=Depends(get_current_user)):
    habits = await db.habits.find({"user_id": user["_id"]}).to_list(100)
    result = []
    for h in habits:
        filtered = [d for d in h["completions"] if start <= d <= end]
        result.append({h["name"]: filtered})
    return result

@router.get("/habits/missed")
async def missed_today(user=Depends(get_current_user)):
    today = date.today().isoformat()
    habits = await db.habits.find({"user_id": user["_id"]}).to_list(100)
    missed = []
    for h in habits:
        if today not in h["completions"]:
            missed.append(h["name"])
    return missed
