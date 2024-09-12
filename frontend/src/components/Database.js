const sampleChatData = require('../data/sample_chat.json');
const sampleEventData = require('../data/sample_events.json');
const sampleTodoData = require('../data/sample_todo.json');

const USERNAME = "user1"


class Database {
  constructor() {
    this.chatMessages = [];
    this.calendarEvents = [];
    this.todoList = [];
  }

  processServerMessage(message) {
    const data = JSON.parse(message);
    if ('chat' in data) {
      this.chatMessages = data['chat']
    }
    if ('events' in data) {
      this.calendarEvents = data['events']
    }
    if ('todo' in data) {
      this.todoList = data['todo']
    }
  }

  addChatMessage(message) {
    this.chatMessages.push(message);
  }

  addCalendarEvent(event) {
    this.calendarEvents.push(event);
  }

  addTodoItem(task) {
    this.todoList.push(task);
  }

  getChatMessages() {
    return this.chatMessages;
  }

  getCalendarEvents() {
    return this.calendarEvents;
  }

  getTodoList() {
    return this.todoList;
  }

  loadSampleData() {
    this.chatMessages = sampleChatData;
    this.calendarEvents = sampleEventData;
    this.todoList = sampleTodoData;
  }
}

export default Database;
