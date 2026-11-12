function queue(worker, concurrency) {
  const pending = [];
  let running = 0;
  function next() {
    if (running >= concurrency || pending.length === 0) return;
    running++;
    const [task, done] = pending.shift();
    worker(task).then(done).finally(() => { running--; next(); });
  }
  return { push: (task) => new Promise((done) => { pending.push([task, done]); next(); }) };
}

module.exports = { queue };
