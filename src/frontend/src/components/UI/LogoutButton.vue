<template>
    <div class="button-wrapper" @click="$emit('click')">
        <img src="/img/logout-logo.svg">
        <p>выход</p>
    </div>
</template>
<script>
export default {
    name: "logout-button",
    emits: ['click']
}
</script>
<style scoped>
.button-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 2px;
    cursor: pointer;
    user-select: none;
    transition: 0.5s;
    -webkit-transition: 0.5s;
}
.button-wrapper:hover {
    transition: 0.5s;
    -webkit-transition: 0.5s;
    transform: scale(1.05);
}
.button-wrapper p {
    font-size: 18px;
    font-family: Stolzl;
    font-weight: 400;
    margin: 0;
    color: #FF0038;
}
.button-wrapper img {
    width: 44px;
    height: 44px;
}
</style>