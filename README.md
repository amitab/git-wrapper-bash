# Git Wrapper Bash
A mini project of mine to speed up my git workflow, focusing specifically
on local branches and their histories to create patches.

## What is it?
1. A wrapper over git to manage and maintain your local repositories.
2. Create a full branch history diff without you having to remember 
   the branch's parent
3. Quickly create a Bug/Worklog Branch
4. List all the Bug branches or Worklog branches seperately
5. Maintain a record of all references and their approximate start commit

## Known Issues
When two references point to the same commit, I am not able to tell which one
was there first.

## Future Enhancements
Not be tied down by just the two types of branches - Bug or Worklog. It should
be able to have a customizable types of branches so that different types of 
branch templates can be added on the fly