(() => {
 document.querySelector('.cch-hero-scroll')?.addEventListener('click',event=>{const target=document.querySelector('#cch-reasons');if(target){event.preventDefault();event.stopPropagation();window.scrollTo({top:target.getBoundingClientRect().top+window.scrollY,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});}});
 const video=document.querySelector('#cch-hero video'),button=document.querySelector('.cch-video-toggle');
 if(!video||!video.getAttribute('src'))return;
 const reduced=matchMedia('(prefers-reduced-motion:reduce)');
 function sync(){button.textContent=video.paused?'動画を再生':'動画を一時停止'}
 button.hidden=false;
 button.addEventListener('click',()=>video.paused?video.play().catch(sync):video.pause());
 video.addEventListener('play',sync);video.addEventListener('pause',sync);
 video.addEventListener('error',()=>{button.hidden=true;document.querySelector('.cch-video-caption').hidden=false});
 if(!reduced.matches)video.play().catch(sync);
 reduced.addEventListener('change',()=>{if(reduced.matches)video.pause()});sync();
})();
