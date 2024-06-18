<template>
    <div class="cross-wrapper">
        <div class="c"></div>
        <div class="c"></div>
    </div>
</template>
<script>
export default {
    name: "window-cross"
}
</script>
<style>
    .cross-wrapper {
        width: 30px;
        height: 30px;
        background-color: rgb(223, 223, 223);
        border-radius: 15px;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    .c {
        position: absolute;
        width: 1.5px;
        height: 40%;
        background-color: black;
    }
    .c:nth-child(0) {
        transform: rotate(90);
    }
</style>