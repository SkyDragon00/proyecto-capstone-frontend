document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('events-container');
  
    const sampleEvents = [
      {
        id: 4,
        title: "Science Fair",
        date: "Nov 8, 2023 • 11:00 AM",
        location: "Science Building",
        description: "Showcase of student research projects across all scientific disciplines."
      },
    ];
  
    // Load template
    const res = await fetch('components/event-card.html');
    const template = await res.text();
  
    sampleEvents.forEach(event => {
      let cardHTML = template
        .replace('{{title}}', event.title)
        .replace('{{date}}', event.date)
        .replace('{{location}}', event.location)
        .replace('{{description}}', event.description)
        .replace('{{id}}', event.id);
  
      const wrapper = document.createElement('div');
      wrapper.innerHTML = cardHTML.trim();
  
      container.appendChild(wrapper.firstChild);
    });
  });
  