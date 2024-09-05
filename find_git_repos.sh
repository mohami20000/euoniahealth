#!/bin/bash

echo "Adding .gitignore file..."
git add .gitignore
git commit -m "Add .gitignore file"

echo "Organizing project structure..."
mkdir -p ai-mindfulness-coach
git mv * ai-mindfulness-coach/ 2>/dev/null
git mv .* ai-mindfulness-coach/ 2>/dev/null
mv ai-mindfulness-coach/.gitignore .
git add .
git commit -m "Organize project structure"

echo "Pushing changes to GitHub..."
git push origin main --force

echo "Project reorganized and pushed to GitHub."