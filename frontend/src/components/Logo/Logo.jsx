import YoshiPhone from "../../static/Yoshi-phone.png";

function Logo(props) {
  return (
    <div className="logo">
      <img src={YoshiPhone} alt="Yoshi Phone" height={props.size} width={props.size}/>
    </div>
  )
}

export default Logo;