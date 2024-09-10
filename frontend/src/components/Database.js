const sampleChatData = require('../data/sample_chat.json');
const sampleEventData = require('../data/sample_events.json');
const sampleTodoData = require('../data/sample_todo.json');

class Database {
  constructor() {
    this.chatMessages = [];
    this.calendarEvents = [];
    this.todoList = [];
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
