from pydantic import BaseModel
from typing import Optional, List

class ErrorResponse(BaseModel):
    error: str

class NicheDiscoveryResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

class NicheDiscoveryRequest(BaseModel):
    niche: str
    keywords: List[str]
    target_audience: str
    budget: float
    duration: int

class DailyNicheReportResponse(BaseModel):
    date: str
    niche: str
    performance: dict

class WebsiteCreationRequest(BaseModel):
    domain: str
    content: str
    design: Optional[str] = None
    budget: float
    deadline: str

class WebsiteCreationResponse(BaseModel):
    success: bool
    website_url: Optional[str] = None
    error: Optional[str] = None

class WebsiteMimicRequest(BaseModel):
    source_url: str
    target_domain: str
    budget: float
    deadline: str

class WebsiteIdentifierRequest(BaseModel):
    domain: str

class WebsiteViewResponse(BaseModel):
    domain: str
    content: str
    design: Optional[str] = None

class WebsiteStatusResponse(BaseModel):
    domain: str
    status: str

class WebsiteAnalyticsResponse(BaseModel):
    domain: str
    analytics_data: dict

class WebsiteMonetizationResponse(BaseModel):
    domain: str
    monetization_data: dict

class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    budget: float
    deadline: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    budget: float
    deadline: str

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]

class TaskStatusResponse(BaseModel):
    task_id: int
    status: str
    details: Optional[str] = None

class WebhookRegisterRequest(BaseModel):
    url: str
    event: str

class WebhookResponse(BaseModel):
    id: int
    url: str
    event: str

class LLMProviderSwitchRequest(BaseModel):
    provider: str

class MessageResponse(BaseModel):
    message: str
