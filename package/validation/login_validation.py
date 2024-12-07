from fastapi import Body, HTTPException, Request
from package.database_management.data_models import CodeModel, LoginFormat, UserModel
from package.ezorm.crud import Create, Read, Update

from package.routes.authorizer.utils import generate_code

def validate_login_request(request:Request, user:LoginFormat=Body(...)):
    user_data = Read(UserModel(username=user.username))
    
    if user_data.shape[0]==0:
        raise HTTPException(status_code=400, detail=f"User '{user.username}' not found.")
    elif user_data['password'].values[0] != user.password:
        raise HTTPException(status_code=400, detail=f"Incorrect password.")
    elif user_data.shape[0]>1:
        raise HTTPException(status_code=400, detail=f"User '{user.username}' duplicated.")
    
    user_model = UserModel(**user_data.iloc[0].to_dict())
    code = generate_code()
    existing_code_model = CodeModel(client_id=user_model.client_id)
    new_code_model = CodeModel(client_id=user_model.client_id, code=code, code_challenge=user.code_challenge)
    
    if Read(existing_code_model).shape[0]==0:
        Create(new_code_model)
    elif Read(existing_code_model).shape[0]==1:
        Update(existing=existing_code_model, new=new_code_model)
    elif Read(existing_code_model).shape[0]>1:
        raise HTTPException(status_code=400, detail=f"Client duplicated.")
    
    return new_code_model
    
    