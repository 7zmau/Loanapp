# Loanapp API
This is the thing I created for my job application.
### Create docker image
`docker build -t loanapp .`
### Run the container
`docker run -dp 3500:80 loanapp`<br>
Open browser at http://localhost:3500
### Run the tests
 `docker exec <container-id> python test.py`
####  To get the Container ID
`docker ps`<br><br>
Copy the Container ID under the 'CONTAINER ID' column.<br>
### API Reference
#### Create a user
|Endpoint URL|Headers|Body|Description|
|:---|:---|:---|:---|
|POST /users  | |{'name': <-name->, 'password': <-password->} |Creates a user with that name and password| <br>
#### Create an admin
Open a bash shell in the container<br>
`docker exec -it <container-id> /bin/bash`<br>
In the container's bash shell <br>
`flask create-admin`<br>

#### API Endpoints
To login <br>

|Endpoint URL|Authorization|Headers|Description|
|:---|:---|:---|:---|
|GET /users/login |Basic Auth| |Returns a token which should be passed as a value to the 'x-access-token' header | <br>

|Endpoint URL|Headers|Body|Description
|:---|:---|:---|:---|
|GET /users | x-access-token| |Returns all users if admin or agent, otherwise returns that particular user. |<br>
|GET /users/:user-id |x-access-token| |Get user with that ID |<br>
|PATCH /users/:user-id |x-access-token| |Promote a user to an agent. |<br>
|DELETE /users/:user-id |x-access-token| |Delete a user |<br>
|GET /loans/get-interest-rates | |{'tenure': <-tenure in months-> |Get interest rates |<br>
|GET /loans/get-loan-info | |{'amount': <-amount->, 'tenure': <-tenure in months->} |Get loan info. | <br>
|GET /loans |x-access-token | |Get all loans if admin or agent, otherwise gets that user's loans |<br>
|POST /loans/request | x-access-token|{'application-id': <-application-id->, 'user-id': <-user-id->} |Request for a loan on behalf of the user. |<br>
|PUT /loans/approve |x-access-token |{'loan-id': <-loan-id->, 'user-id': <-user-id->} |Approve a loan request. Can be done by an admin only. |<br>
|POST /loans/apply |x-access-token |{'amount': <-amount->, 'tenure': <-tenure in months->} | Apply for a loan. Can be done by the user. |<br>
|GET /loans/view-applications|x-access-token| | View loan applications. Returns applications along with application ID which can be used to request a loan by agent. |<br>
|PUT /loans/edit/:loan-id|x-access-token|{'amount': <-amount->, 'tenure': <-tenure in months->} |Edit a loan. Input is the new loan amount and tenure. Loan cannot be edited if already approved. | <br>
