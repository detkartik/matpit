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

<img width="1680" alt="Screenshot 2021-10-02 at 1 23 08 PM" src="https://user-images.githubusercontent.com/13103243/136732758-5e797495-57d1-48f6-85d1-173fc437f70a.png">

<img width="1680" alt="Screenshot 2021-10-04 at 11 30 23 PM" src="https://user-images.githubusercontent.com/13103243/136732765-7034cf2c-3d40-48da-8e4a-e61ad8399603.png">

<img width="1680" alt="Screenshot 2021-10-04 at 11 30 27 PM" src="https://user-images.githubusercontent.com/13103243/136732767-581ca45a-afdc-4385-ad20-c90b92a726a4.png">

<img width="1680" alt="Screenshot 2021-10-04 at 11 30 53 PM" src="https://user-images.githubusercontent.com/13103243/136732771-d1f02f64-cc15-461e-8e93-e3957f4daed2.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 31 21 AM" src="https://user-images.githubusercontent.com/13103243/136732774-285a5ac8-1886-430c-95bd-073cec8a9864.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 31 28 AM" src="https://user-images.githubusercontent.com/13103243/136732777-0073f3cd-cba0-4fec-8481-2bfa8f75ef5e.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 31 32 AM" src="https://user-images.githubusercontent.com/13103243/136732780-e785dd31-1d06-499a-948c-3a7f20f734e4.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 31 36 AM" src="https://user-images.githubusercontent.com/13103243/136732792-69d9c553-52fa-4b60-81d2-04c0a337c1ae.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 33 06 AM" src="https://user-images.githubusercontent.com/13103243/136732806-ead39833-db4d-45bd-8461-881b340741c6.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 33 09 AM" src="https://user-images.githubusercontent.com/13103243/136732820-0fbfa9e6-dc02-4a08-8b90-821793be4b12.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 33 17 AM" src="https://user-images.githubusercontent.com/13103243/136732825-eedf58c2-cb2c-4e12-83ac-739d79dca9f7.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 33 22 AM" src="https://user-images.githubusercontent.com/13103243/136732831-f0355d88-95e2-413d-9780-ce7b738eba40.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 33 24 AM" src="https://user-images.githubusercontent.com/13103243/136732841-06de43d2-9717-4a43-b2e1-0903e1e87e0a.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 33 30 AM" src="https://user-images.githubusercontent.com/13103243/136732843-af7e93ad-1aa9-4ed3-b45d-badec17fe251.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 33 33 AM" src="https://user-images.githubusercontent.com/13103243/136732862-b301db66-06ca-4bce-91dc-592fdd464946.png">

<img width="1680" alt="Screenshot 2021-10-05 at 8 33 38 AM" src="https://user-images.githubusercontent.com/13103243/136732876-5c475630-8d16-4d70-85c7-b859f7b2f636.png">

<img width="1676" alt="Screenshot 2021-10-11 at 9 25 28 AM" src="https://user-images.githubusercontent.com/13103243/136732886-9951e7c6-167e-49e7-812b-424692ad8f57.png">

<img width="1653" alt="Screenshot 2021-10-11 at 9 25 41 AM" src="https://user-images.githubusercontent.com/13103243/136732890-90bbbfb7-db36-4267-9b54-577188bdad80.png">

<img width="1679" alt="Screenshot 2021-10-11 at 9 25 56 AM" src="https://user-images.githubusercontent.com/13103243/136732891-f3c78970-498a-4a70-9baf-c23c44526ee2.png">

<img width="1680" alt="Screenshot 2021-10-11 at 9 26 02 AM" src="https://user-images.githubusercontent.com/13103243/136732910-53fee3c3-c7e3-4cc7-a656-b93f0946aee7.png">

<img width="1678" alt="Screenshot 2021-10-11 at 9 26 10 AM" src="https://user-images.githubusercontent.com/13103243/136732926-f552b6c0-02c9-4dbf-8547-9c506555e496.png">

<img width="11" alt="Screenshot 2021-10-11 at 9 26 46 AM" src="https://user-images.githubusercontent.com/13103243/136732929-3da7969b-b0fd-49ed-85a4-c89a7db944cf.png">

<img width="1678" alt="Screenshot 2021-10-11 at 9 26 55 AM" src="https://user-images.githubusercontent.com/13103243/136732931-e118eeb1-aa57-443b-a1ad-9469c432bd2f.png">

<img width="1680" alt="Screenshot 2021-10-11 at 9 27 09 AM" src="https://user-images.githubusercontent.com/13103243/136732937-c0e9db3b-9b44-4bad-b045-cf1700ecbda9.png">

<img width="1677" alt="Screenshot 2021-10-11 at 9 27 24 AM" src="https://user-images.githubusercontent.com/13103243/136732942-eb6d7c9e-6fd0-41f0-89d3-3ec796bf7f7c.png">

<img width="1675" alt="Screenshot 2021-10-11 at 9 27 42 AM" src="https://user-images.githubusercontent.com/13103243/136732944-db3aed6d-f8cb-46f3-a190-e9429448ff77.png">
[service.pdf](https://github.com/detkartik/matpit/files/7319533/service.pdf)





  
