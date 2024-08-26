<template>
	<div class="checkbox-wrapper">
		<input :id="props.id" type="checkbox" v-model="checked" @click.stop />
	</div>
</template>
<script lang="ts">
export default {
	name: "table-checkbox",
};
</script>
<script setup lang="ts">
const props = defineProps({
	id: {
		type: String,
		required: true,
	},
});
const checked = defineModel("checked");
</script>
<style scoped>
.checkbox-wrapper {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 18px;
	height: 18px;
}

input {
	width: 17px;
	height: 17px;
	border: 2px solid #7f7f7f;
	border-radius: 3.5px;
	-webkit-appearance: none;
	appearance: none;
}

input[type="checkbox"]:checked {
	background-image: url("/img/check-box-checked.svg");
	background-size: cover;
	/* background-color: #993ca6; */
	border-color: #993ca6;
}
</style>
