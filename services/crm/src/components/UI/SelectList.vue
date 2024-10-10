<template>
	<ul class="list-wrapper">
		<li
			v-for="(record, index) in props.selectList"
			@click.prevent="emit('select', index)"
			:tabindex="index"
			:key="index"
		>
			{{ record }}
		</li>
	</ul>
</template>
<script setup lang="ts">
const props = defineProps({
	selectList: {
		type: Array<String>,
		required: true,
	},
});
const emit = defineEmits(["select"]);
</script>
<script lang="ts">
export default {
	name: "select-list",
};
</script>
<style scoped>
.list-wrapper::-webkit-scrollbar {
	width: 5px;
	height: 5px;
	border-radius: 2000px;
}

.list-wrapper::-webkit-scrollbar-track {
	background-color: #e7e7e7;
	margin-bottom: 10px;
}

.list-wrapper::-webkit-scrollbar-thumb:vertical {
	height: 10px;
	width: 5px;
	height: 15px !important;
	border-radius: 22px;
	background-color: #993ca6;
}
.list-wrapper {
	display: flex;
	flex-direction: column;
	align-self: center;
	min-width: calc(100% - 20px);
	border: 1px solid #e8e8e8;
	border-top: none;
	border-bottom-left-radius: 10px;
	border-bottom-right-radius: 10px;
	max-height: 120px;
	overflow: auto;

	margin: 0;
	padding-left: 0;
}

li {
	padding-top: 6px;
	padding-bottom: 6px;
	padding-left: 15px;
	padding-right: 15px;
	list-style: none;
	width: 100%;
	font-family: Stolzl;
}
li:hover {
	background-color: #fdf7fd;
	cursor: pointer;
	outline: none;
}
li:focus {
	background-color: #fdf7fd;
	outline: none;
}
</style>
