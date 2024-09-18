import React, { useEffect, useRef, useState } from 'react';
import { useDataContext } from "./DataProvider";

// CSS consts
const scrollBarWidth = '17px';
const cellHeightPx = 50;
const borderHeightPx = 1;
const totalCellHeight = cellHeightPx + borderHeightPx;
const borderStyle = `${borderHeightPx}px solid #ddd`;

// Logic consts
const date_format = { weekday: 'short', month: 'numeric', day: 'numeric' };

// Helper function to get the next 7 days
const getNext7Days = (date) => {
  const days = []; // Initialize with an empty string for the time column
  const dayOffset = (date.getDay() === 0 ? -6 : 1) - date.getDay(); // Calculate offset to get to Monday
  date.setDate(date.getDate() + dayOffset); // Set today to the nearest Monday

  for (let i = 0; i < 7; i++) {
    const day = new Date(date);
    day.setDate(date.getDate() + i);
    days.push(day.toLocaleDateString('en-US', date_format));
  }

  return days;
};

// Helper function to get time slots
const getTimeSlots = () => {
  const times = [];
  for (let hour = 0; hour < 24; hour++) {
    const time = new Date();
    time.setHours(hour, 0, 0, 0);
    times.push(time.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true }));
  }
  return times;
};

function Calendar() {
  const { data } = useDataContext();
  const [startDate, setStartDate] = useState(new Date());
  const [days, setDays] = useState(getNext7Days(startDate));

  // Scroll to the current time anyitme the data changes
  const scrollContainerRef = useRef(null);
  useEffect(() => {
    if (scrollContainerRef.current) {
      const currentHour = new Date().getHours();
      const scrollToPosition = currentHour * totalCellHeight;
      scrollContainerRef.current.scrollTop = scrollToPosition;
    }
  }, [data]);

  const timeSlots = getTimeSlots();

  const calculateEventPosition = (event) => {
    const eventStartTime = new Date(event.start);
    const eventEndTime = new Date(event.end);

    // Get the day index (0-6, starting with Sunday)
    const startDayIndex = eventStartTime.getDay();
    const startHour = eventStartTime.getHours();
    const startMinutes = eventStartTime.getMinutes();
    const endHour = eventEndTime.getHours();
    const endMinutes = eventEndTime.getMinutes();

    const top = (startHour + startMinutes / 60) * totalCellHeight;
    const totalMinutes = (endHour * 60 + endMinutes) - (startHour * 60 + startMinutes);
    const height = (totalMinutes / 60) * totalCellHeight;
    return { startDayIndex, top, height };
  };

  const handleDateChange = (date) => {
    setStartDate(date);
    setDays(getNext7Days(date));
  };

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Calendar Header, will take up as much space as needed */}
      <div style={{
        width: '100%',
        // TODO: make it fill as much as it needs and let the cal take the rest without a max height
        maxHeight: '20%',
        textAlign: 'center',
      }}>
        <input
          type="date"
          value={startDate.toISOString().split('T')[0]} // Format date to YYYY-MM-DD
          onChange={(e) => handleDateChange(new Date(e.target.value))}
        />
        <button
          onClick={() => handleDateChange(new Date())}
        >
          Today
        </button>
      </div>
      <div style={{
        width: '100%',
        minHeight: '80%',
      }}>
        {/* Container div to account for calendar scroll bar */}
        <div style={{
          width: `calc(100% - ${scrollBarWidth})`,
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
        }}>
          {/* Date Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            borderLeft: borderStyle,
            marginLeft: '12.5%',
          }}>
            {days.map((day, index) => (
              <div
                key={index}
                style={{
                  textAlign: 'center',
                  flex: 1,
                  padding: '20px 0',
                  borderRight: borderStyle,
                }}
              >
                {day}
              </div>
            ))}
          </div>

          {/* Time Grid with Events */}
          <div
            ref={scrollContainerRef}
            style={{
              display: 'flex',
              overflowY: 'scroll',
              marginRight: `-${scrollBarWidth}`,
              width: `calc(100% + ${scrollBarWidth})`,
              borderTop: borderStyle,
              position: 'relative',
            }}>
            {/* Time Column */}
            <div style={{
              width: '12.5%',
            }}>
              {timeSlots.map((time, index) => (
                <div
                  key={index}
                  style={{
                    height: `${cellHeightPx}px`,
                    borderBottom: borderStyle,
                    display: 'flex',
                    alignItems: 'flex-start', // Align time to the top of each block
                    justifyContent: 'center',
                    fontSize: '12px',
                  }}
                >
                  {time}
                </div>
              ))}
            </div>

            {/* Time Grid */}
            <div style={{
              display: 'flex',
              width: '87.5%',
            }}>
              {days.map((day, dayIndex) => (
                <div
                  key={dayIndex}
                  style={{
                    flex: 1,
                    position: 'relative',
                  }}
                >
                  {timeSlots.map((_, timeIndex) => (
                    <div
                      key={timeIndex}
                      style={{
                        height: `${cellHeightPx}px`,
                        borderBottom: borderStyle,
                        borderLeft: borderStyle,
                        backgroundColor: timeIndex % 2 === 0 ? '#f9f9f9' : '#fff',
                      }}
                    />
                  ))}

                  {/* Render Events */}
                  {data.events
                    .filter(event => {
                      const eventStartTime = new Date(event.start);
                      return eventStartTime.toLocaleDateString('en-US', date_format) === day;
                    })
                    .map((event, index) => {
                      const { startDayIndex, top, height } = calculateEventPosition(event);

                      return (
                        <div
                          key={index}
                          style={{
                            position: 'absolute',
                            top: `${top}px`,
                            height: `${height}px`,
                            width: '100%',
                            backgroundColor: 'rgba(0, 123, 255, 0.5)',
                            border: '1px solid #007bff',
                            borderRadius: '4px',
                            padding: '2px',
                            boxSizing: 'border-box',
                          }}
                        >
                          {event.summary}
                        </div>
                      );
                    })}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div> {/* End of calendar grid */}
    </div>
  );
}

export default Calendar;
