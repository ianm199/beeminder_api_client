from typing import Optional, List, Tuple, Dict, Union
from pydantic import BaseModel

class Datapoint(BaseModel):
    """
    A single datapoint for a Beeminder goal.
    """
    id: Optional[str]
    timestamp: Optional[int]
    daystamp: Optional[str]
    value: Optional[float]
    comment: Optional[str]
    updated_at: Optional[int]
    requestid: Optional[str]

class Contract(BaseModel):
    """
    A contract related to a Beeminder goal's pledge.
    """
    amount: Optional[float]
    stepdown_at: Optional[int]

class BeeminderGoal(BaseModel):
    """
    A Pydantic model representing the attributes of a Beeminder goal.
    """
    slug: Optional[str] = None
    updated_at: Optional[int] = None
    title: Optional[str] = None
    fineprint: Optional[str] = None
    yaxis: Optional[str] = None
    goaldate: Optional[int] = None
    goalval: Optional[float] = None
    rate: Optional[float] = None
    runits: Optional[str] = None
    svg_url: Optional[str] = None
    graph_url: Optional[str] = None
    thumb_url: Optional[str] = None
    autodata: Optional[str] = None
    goal_type: Optional[str] = None
    losedate: Optional[int] = None
    urgencykey: Optional[str] = None
    queued: Optional[bool] = None
    secret: Optional[bool] = None
    datapublic: Optional[bool] = None
    datapoints: Optional[List[Datapoint]] = None
    numpts: Optional[int] = None
    pledge: Optional[float] = None
    initday: Optional[int] = None
    initval: Optional[float] = None
    curday: Optional[int] = None
    curval: Optional[float] = None
    currate: Optional[float] = None
    lastday: Optional[int] = None
    yaw: Optional[int] = None
    dir: Optional[int] = None
    lane: Optional[int] = None
    mathishard: Optional[List[Optional[float]]] = None
    headsum: Optional[str] = None
    lumsum: Optional[str] = None
    kyoom: Optional[bool] = None
    odom: Optional[bool] = None
    aggday: Optional[str] = None
    steppy: Optional[bool] = None
    rosy: Optional[bool] = None
    movingav: Optional[bool] = None
    aura: Optional[bool] = None
    frozen: Optional[bool] = None
    won: Optional[bool] = None
    lost: Optional[bool] = None
    maxflux: Optional[int] = None
    contract: Optional[Contract] = None
    road: Optional[List[Tuple[Optional[int], Optional[float], Optional[float]]]] = None
    roadall: Optional[List[Tuple[Optional[int], Optional[float], Optional[float]]]] = None
    fullroad: Optional[List[Tuple[Optional[int], Optional[float], Optional[float]]]] = None
    rah: Optional[float] = None
    delta: Optional[float] = None
    delta_text: Optional[str] = None
    safebuf: Optional[int] = None
    safebump: Optional[float] = None
    autoratchet: Optional[int] = None
    id: Optional[str] = None
    callback_url: Optional[str] = None
    description: Optional[str] = None
    graphsum: Optional[str] = None
    lanewidth: Optional[float] = None
    deadline: Optional[int] = None
    leadtime: Optional[int] = None
    alertstart: Optional[int] = None
    plotall: Optional[bool] = None
    last_datapoint: Optional[Datapoint] = None
    integery: Optional[bool] = None
    gunits: Optional[str] = None
    hhmmformat: Optional[bool] = None
    todayta: Optional[bool] = None
    weekends_off: Optional[bool] = None
    tmin: Optional[str] = None
    tmax: Optional[str] = None
    tags: Optional[List[str]] = None


class BeeminderUser(BaseModel):
    """
    A Pydantic model representing a Beeminder user based on the actual API schema.
    Only username, goals, created_at, and updated_at are required.
    Allows extra fields from the API response.
    """
    username: str
    goals: List[str]
    created_at: int
    updated_at: int
    timezone: Optional[str] = None
    urgency_load: Optional[float] = None
    deadbeat: Optional[bool] = None
    has_authorized_fitbit: Optional[bool] = None
    default_leadtime: Optional[int] = None
    default_alertstart: Optional[int] = None
    default_deadline: Optional[int] = None
    subscription: Optional[str] = None
    subs_downto: Optional[str] = None
    subs_freq: Optional[int] = None
    subs_lifetime: Optional[str] = None
    remaining_subs_credit: Optional[int] = None
    id: Optional[str] = None

    class Config:
        extra = "allow"


class Datapoint(BaseModel):
    """
    An expanded Pydantic model representing a Beeminder datapoint.
    All fields are optional except value, following the API schema.
    """
    id: Optional[str] = None
    timestamp: Optional[int] = None
    daystamp: Optional[str] = None
    value: float
    comment: Optional[str] = None
    requestid: Optional[str] = None
    updated_at: Optional[int] = None

    class Config:
        extra = "allow"