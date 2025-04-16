document.addEventListener('DOMContentLoaded', () => {
    const eventModal = document.getElementById('event-modal');
    const closeModalBtn = document.getElementById('close-modal');
  
    // Modal event binding (delegated later for dynamic events)
    function openModal(eventData) {
      document.getElementById('modal-title').textContent = eventData.title;
      document.getElementById('modal-date').textContent = eventData.date;
      document.getElementById('modal-location').textContent = eventData.location;
      document.getElementById('modal-description').textContent = eventData.description;
      document.getElementById('modal-image').src = eventData.image;
  
      const scheduleList = document.getElementById('modal-schedule');
      scheduleList.innerHTML = '';
      eventData.schedule.forEach(item => {
        const li = document.createElement('li');
        li.className = 'flex items-start';
        li.innerHTML = `
          <span class="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-sm mr-3">${item.time}</span>
          <span>${item.activity}</span>
        `;
        scheduleList.appendChild(li);
      });
  
      eventModal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    }
  
    function closeModal() {
      eventModal.classList.add('hidden');
      document.body.style.overflow = 'auto';
    }
  
    closeModalBtn?.addEventListener('click', closeModal);
  
    eventModal?.addEventListener('click', (e) => {
      if (e.target === eventModal) {
        closeModal();
      }
    });
  
    // Dummy event data map (replace with real API or logic)
    const eventDataMap = {
      1: {
        title: "Annual Tech Symposium",
        date: "Oct 15, 2023 • 9:00 AM",
        location: "Main Auditorium",
        description: "Join us for the biggest technology conference of the year featuring industry leaders and innovative research. This year's theme is 'The Future of AI in Society'.",
        image: "https://images.unsplash.com/photo-1524179091875-bccc9e37a1d1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80",
        schedule: [
          { time: "9:00 AM", activity: "Registration & Breakfast" },
          { time: "10:00 AM", activity: "Opening Keynote: Dr. Jane Smith" },
          { time: "11:30 AM", activity: "Panel Discussion: Ethical AI" },
          { time: "1:00 PM", activity: "Lunch Break" },
          { time: "2:30 PM", activity: "Workshops (3 tracks)" },
          { time: "4:30 PM", activity: "Closing & Networking" }
        ]
      },
      2: {
        title: "Career Fair 2023",
        date: "Nov 5, 2023 • 10:00 AM",
        location: "Student Center",
        description: "Connect with top employers and explore internship and job opportunities across various industries.",
        image: "https://images.unsplash.com/photo-1540575467063-178a50c2df87?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80",
        schedule: [
          { time: "10:00 AM", activity: "Doors Open" },
          { time: "10:30 AM", activity: "Company Presentations" },
          { time: "12:00 PM", activity: "Lunch Break" },
          { time: "1:00 PM", activity: "Resume Reviews" },
          { time: "2:30 PM", activity: "Mock Interviews" },
          { time: "4:00 PM", activity: "Networking" }
        ]
      },
      3: {
        title: "Winter Music Festival",
        date: "Dec 10, 2023 • 6:00 PM",
        location: "University Quad",
        description: "Enjoy performances by student bands and special guests at our annual music celebration.",
        image: "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80",
        schedule: [
          { time: "6:00 PM", activity: "Gates Open" },
          { time: "6:30 PM", activity: "Jazz Ensemble" },
          { time: "7:15 PM", activity: "University Choir" },
          { time: "8:00 PM", activity: "Band Showcase" },
          { time: "9:00 PM", activity: "Fireworks" }
        ]
      }
    };
  
    // Event delegation
    document.body.addEventListener('click', (e) => {
      const target = e.target.closest('.event-details-btn');
      if (target) {
        const id = target.dataset.eventId;
        const eventData = eventDataMap[id];
        if (eventData) openModal(eventData);
      }
    });
  });
  