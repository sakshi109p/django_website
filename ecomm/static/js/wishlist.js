var updateBtns = document.getElementsByClassName('update-wishlist')

for(var i=0;i<updateBtns.length;i++)
{
    console.log('HI WISHLIST BUTTON')
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('Clickeddd')
        var url = '/update-wishlist/'
        
        fetch(url, {
            mode: 'cors',
            method: 'POST',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken':csrftoken,
            },
            body: JSON.stringify({'productId' : productId, 'action': action})
            })
            .then((response) =>{
                return response.json()
            })
            .then((data) =>{
                console.log('data:',data)
                location.reload()
            })
    })
}