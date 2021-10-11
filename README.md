# matpit
Matpit consultency
### Project Setup for Mac

- Install python
  ```sh
  brew install python3
  ```
- Install mysql
  ```sh
  brew install msqlclient
  ```
- Start mysql
  ```sh
  brew services start mysql
  ```

- Clone project
  ```sh
  git clone git@github.com:detkartik/matpit.git
  cd matpit/
  ```
- Create virtualenv
  ```sh
  brew install mkvirtualenv
  mkvirtualenv --python=/usr/local/bin/python3 matpit
  workon matpit
  ```
- Install packages
  ```sh
  pip install -r requirements.txt
  ```
- To run the project
  ```sh
  cd matpit
  python manage.py migrate
  python manage.py collectstatic
  python manage.py createsuperuser
  python manage.py runserver
  ```

### Project Setup for Ubuntu

- Install Python

```sh
Sudo apt install python3.7
```


- Clone project

```sh
git clone git@github.com:detkartik/matpit.git
cd credtest/
```

- Create virtualenv

```sh
sudo apt-get install python-pip
sudo pip install virtualenv
mkdir ~/.virtualenvs
sudo pip install virtualenvwrapper
export WORKON_HOME=~/.virtualenvs
. /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv matpit
workon matpit
OR pipenv shell
pip install -r requirements.txt
```


- To run the project

```sh
cd matpit
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py runserver
```

- Git Commands to push and pull -

```sh
 
    For Local -
    cd matpit
    git add "changes"
    git commit -am "commit message"
    git pull origin 'branch name'
    git checkout -b 'new branch name'
    git stash
    git push origin -u 'branch name'

    GITHUB -
    Login to github
    Review and create a PR
    Merge the PR to main branch


   For Server -
    cd django/
    source venv/bin/activate
    Git pull origin main
    Python3 manage.py makemigrations
    Python3 manage.py migrate
    sudo apache2ctl restart

 
 
  ```
- Process
```sh

1. Roles -
'ADMIN','ACCOUNT’,'BO',
'BH','AFM','AF',
'AM','ZSM’,'RSM','ASM','SM','RM','DSA','CONNECTOR'

2. ADMIN ( Super User) - should be always Verified, Referred By ADMIN itself , Admin can Register All the respective Roles
Back Office - Back office user should always be created by ADMIN or another Back Office  to Verify and Reject the user documents
User Manager - Should be able to Suspend, Reactivate and Verify the details of follow employees ( Eg. Connector)  
Verify Service - Service Verification can be done by Manager, Accountant and ADMIN once the Service is submitted successfully


     	
5. Once All Process is Completed Service is created successfully and should be Approved/Rejected By Account Manger ( Role : Account or Admin)

6. If Account Manager Rejects the Service, User should redirect to Disbursement Process and need to provide all relevant docs to satisfy required details

7. Once Approved/Verified By Account Manager the Other Details button should get enabled and Account Manager has to provide Other details such as Incentives, Payout received etc.

8. Further User can chat with Administration Team or Upper Manager by feature Chat displayed in Your Service page

9. User can see the New Service Created or New Chat Appeared from top navbar section displays Notifications related to Service and Chat and can redirect to Your Service page to see all the respective Services and chats

10. Once the Service process is approved Final Result will be Calculated and accessed by Admin/ Account Manager in form of MIC Report

11. MIC Report can be accessed by Upper Managers as well with minimal fields as per the role

12. User Management and Service Management Reports can be accessed by Admin in Report section

13. All Email Notification Related to Verification, Rejection,Approval and Password Reset and Registration should be sent across to respective users

```
- Screenshots & PDF 

<img width="1676" alt="Screenshot 2021-10-11 at 9 25 28 AM" src="https://user-images.githubusercontent.com/13103243/136736549-4e3dfbd5-3cc2-456c-ac45-7fb6cd1f4a1b.png">

<img width="1653" alt="Screenshot 2021-10-11 at 9 25 41 AM" src="https://user-images.githubusercontent.com/13103243/136736562-57f41e8c-fafd-4daf-8816-3c5f6b58c4ea.png">

<img width="1679" alt="Screenshot 2021-10-11 at 9 25 56 AM" src="https://user-images.githubusercontent.com/13103243/136736566-8dabab16-e934-44eb-a2a8-d0a79e9af62b.png">

<img width="1678" alt="Screenshot 2021-10-11 at 9 26 10 AM" src="https://user-images.githubusercontent.com/13103243/136736608-39ce2d07-f924-4337-b4aa-e74ee1ff2c93.png">

<img width="11" alt="Screenshot 2021-10-11 at 9 26 46 AM" src="https://user-images.githubusercontent.com/13103243/136736612-0403216c-78cc-464f-9c55-d3da809eb3c7.png">

<img width="1678" alt="Screenshot 2021-10-11 at 9 26 55 AM" src="https://user-images.githubusercontent.com/13103243/136736613-3ce3ad4f-d698-4943-b493-e1d6bc3dfc5a.png">

<img width="1680" alt="Screenshot 2021-10-11 at 9 27 09 AM" src="https://user-images.githubusercontent.com/13103243/136736615-55f39ca3-bb4a-4824-a901-e0648bcc97c3.png">

<img width="1677" alt="Screenshot 2021-10-11 at 9 27 24 AM" src="https://user-images.githubusercontent.com/13103243/136736618-cd9af369-1672-49e3-bb28-c1565e83b9e6.png">

<img width="1675" alt="Screenshot 2021-10-11 at 9 27 42 AM" src="https://user-images.githubusercontent.com/13103243/136736628-7448b11b-d8bf-437c-8fb6-eacaddad4804.png">








  
