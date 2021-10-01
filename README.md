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

  
